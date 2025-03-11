import os
import pickle
from agent.planner_critic.sender import send_planner_request
from agent.planner_critic.task_manager import turn_text_steps_to_iter
from agent.step_check.sender import send_stepcheck_request
from agent.actor.sender import send_actor_request
from agent.actor_critic.sender import send_actor_critic_request
from agent.utils.log_utils import state_updater
from agent.config import basic_config 


class AutoPCFast:
    def __init__(
        self, 
        software_name=None, 
        project_id=None
    ):        
        self.task_id = f"{software_name}_{project_id}"
        self.cache_folder = os.path.join(basic_config['os_agent_settings']['cache_dir'], "AutoPCFast", self.task_id)
        os.makedirs(self.cache_folder, exist_ok=True)
        print(f"Cache folder: {self.cache_folder}")
        
        self.step = 0
        self.history = []
        self.current_task = None
        self.reset_state()

        self.gui_parser_url = basic_config['gui_parser']['url']
        self.step_check_url = basic_config['step_check']['url']
        self.actor_url = basic_config['actor']['url']
        self.planner_url = basic_config['planner_critic']['url']
        self.actorcritic_url = basic_config['actorcritic']['url']

    @state_updater("Planning ...")
    def run_planner(self, query, software_name, screenshot_path, gui_info, video_path):
        plan = send_planner_request(
            url=self.planner_url,
            screenshot_path=screenshot_path,
            query=query,
            software_name=software_name,
            video_path=video_path,
            task_id=self.task_id,
            gui_info=gui_info
        )

        _, current_task, _ = turn_text_steps_to_iter(plan)
        self.current_task = current_task
        print(f"Current_task: {self.current_task.name}")
        self.update_state({"plan": plan, "current_task": current_task})
        return plan
    
    @state_updater("Running Step-Check ...")
    def run_step_check(self, 
        current_task, 
        parsed_screenshot, 
        screenshot_path, 
        stepcheck_decision, 
        history, 
        software_name, 
        if_screenshot):

        response = send_stepcheck_request(
            url=self.step_check_url,
            current_task=current_task,
            parsed_screenshot=parsed_screenshot,
            screenshot_path=screenshot_path,
            stepcheck_decision=stepcheck_decision,
            history=history,
            software_name=software_name,
            if_screenshot=if_screenshot,
        )
        stepcheck_decision = response.get("stepcheck_decision", None)
        history = response.get("history", [])
        current_task = response.get("current_task", None)
        self.update_state(
            {"stepcheck_decision": stepcheck_decision, 
             "current_task": current_task.name if current_task else None, 
             "history": history}
        )
        return stepcheck_decision, current_task, history

    @state_updater("Running Actor-Critic ...")
    def run_actorcritic(
        self,
        current_task,
        current_action,
        parsed_screenshot,
        screenshot_path,
        software_name,
        if_screenshot):
    
        response = send_actor_critic_request(
            url=self.actorcritic_url,
            current_task=current_task,
            current_action=current_action,
            parsed_screenshot=parsed_screenshot,
            screenshot_path=screenshot_path,
            software_name=software_name,
            history=self.history,
            task_id=self.task_id,
            step_id=self.step,
            if_screenshot=if_screenshot,
        )

        code = response.get("code", "")
        state = response.get("state", "")
        self.update_state(
            {"code": code, 
             "state": state, 
            }
        )

        return code, state

    @state_updater("Running Actor ...")
    def run_actor(
        self,
        current_task,
        parsed_screenshot,
        screenshot_path,
        software_name,
        history,
        if_screenshot=False,
    ):
        response = send_actor_request(
            url=self.actor_url,
            current_task=current_task,
            parsed_screenshot=parsed_screenshot,
            screenshot_path=screenshot_path,
            software_name=software_name,
            history=self.history,
            task_id=self.task_id,
            step_id=self.step,
            if_screenshot=if_screenshot,
        )
        code = response.get("code", None)
        current_task = response.get("current_task", None)
        history = response.get("history", [])
        self.update_state(
            {"code": code, 
             "current_task": current_task.name if current_task else None, 
             "history": history}
        )
        return code, current_task, history

    def run_step(
        self,
        state,
        code,
        current_task,
        last_screenshot_path,
        screenshot_path,
        software_name, 
        if_screenshot=True,
    ):
        
        if state == '<Continue>':
            stepcheck_decision, current_task, history = self.run_step_check(
                current_task=current_task, 
                parsed_screenshot=None,
                screenshot_path=screenshot_path,
                stepcheck_decision='',
                history=self.history,
                software_name=software_name,
                if_screenshot=if_screenshot,
            )

            if stepcheck_decision == '<Finished>':
                state = '<Next>'

        if state == '<Continue>': #
            # Actor
            code, current_task, history = self.run_actor(
                current_task=current_task,
                parsed_screenshot=None,
                screenshot_path=screenshot_path,
                history=self.history,
                software_name=software_name,
                if_screenshot=if_screenshot,
            )

        if state == '<Critic>':
            # Actor-Critic
            critic_output = self.run_actorcritic(
                current_task=current_task,
                current_action=code, 
                parsed_screenshot=None,
                screenshot_path=[last_screenshot_path, screenshot_path],
                software_name=software_name,
                if_screenshot=if_screenshot)

            code, state = critic_output # if correction, code is not "", else code is ""
            # state: critic, next
            if state == '<Next>':
                self.update_history(
                    history=self.history,
                    code=code,
                    state=state,
                    current_task=current_task,
                    screenshot_path=screenshot_path
                )

                return code, state, current_task
            
        # Update history
        self.update_history(
            history=self.history,
            code=code,
            state=state,
            current_task=current_task,
            screenshot_path=screenshot_path
        )

        self.step += 1

        return code, state, current_task

    def update_history(
        self,
        history,
        code,
        state,
        current_task,
        screenshot_path,
        gui=None
    ):

        if state in ["<Critic>"]:
            # the task doesn't change, so only append the code and gui
            self.history[-1]["code"].append(code)
            self.history[-1]["gui"].append(gui)
            self.history[-1]["screenshot_path"].append(screenshot_path)
        elif state in ["<Success>"]:
            pass
        else:
            self.history.append(
                {
                    "task": (
                        current_task
                        if isinstance(current_task, str)
                        else current_task.name
                    ),
                    "code": [code],
                    "gui": [gui],
                    "screenshot_path": [screenshot_path],
                }
            )
        pickle.dump(self.history, open(f"{self.cache_folder}/history.pkl", "wb"))

    def reset(self):
        self.current_task = None
        self.step = 0
        self.history = []
        self.reset_state()

    def reset_state(self):
        self.current_state = {
            "in_progress": False,
            "plan": "",
            "current_step": -1,
            "current_progress": None,
            "current_task": None,
            "code": None,
        }

    def update_state(self, updates):
        for key, value in updates.items():
            if key in self.current_state:
                self.current_state[key] = value
                if key == "current_progress":
                    print(f"Current progress: {value}")

    def get_state(self, key=None):
        return_keys = [
            "in_progress",
            "plan",
            "current_step",
            "current_progress",
            "code",
        ]
        if key:
            return self.current_state.get(key, None)
        else:
            return {k: v for k, v in self.current_state.items() if k in return_keys}

    def generate_task_id(self):
        # Time-based UUID
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        rand_str = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=5))
        self.task_id = f"{timestamp}_{rand_str}"
