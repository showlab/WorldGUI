import os
import re
import json
import glob
import copy
from agent.actor.utils import format_gui, compress_gui
from agent.utils.lmm.run_lmm import run_lmm
from agent.utils.app_functions import run_locateregion

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class StepCheck:
    """Tool that adds the capability to locate image region with a natural language query."""

    name = "stepcheck"
    description = (
        '''pending''')

    def __init__(self, lmm="gpt-4o-2024-08-06"):
        super(StepCheck, self).__init__()
        self.lmm =lmm
        self.software_tips = self.load_software_tips()

    def __call__(
        self,
        current_task,
        parsed_screenshot=None,
        screenshot_path=None,
        stepcheck_decision=None,
        history=None,
        software_name=None,
        if_screenshot=True,
        **kwargs
    ):
        """
        Executes the given task using the provided GUI state and input image. Adjusts the task flow based
        on the execution outcome and prepares the next interaction code.

        Parameters:
            current_task: The current task to be processed.
            gui: Current state of the GUI.
            input_image: An optional screenshot used for updating GUI state.
            history: A list tracking the history of executed tasks and interactions.
            error_message: An optional error message for adjusting task plans.
            next_step: Suggested next step if adjustments are needed.
            pre_act_success_flag: Flag indicating if the previous action was successful.
            pre_act_resume_flag: Flag indicating if the previous action needs resuming.
            software_name: The name of the software being interacted with.
            **kwargs: Additional keyword arguments.

        Returns:
            A tuple containing the interaction code, updated current task, updated history, and a status message.
        """

        # Task Info
        main_goal, finished_tasks, current_task_text, next_task = self.get_task_details(current_task, history)


        tips = self.get_software_tips(self.software_tips, software_name.lower().replace(' ', '_'))

        # step checker before run the actor
        # initial values
        stepcheck_decision = '<Retry>'
        new_screenshot_path = screenshot_path

        iter_idx = 1
        while stepcheck_decision == '<Retry>':

            if iter_idx > 2:
                stepcheck_decision = '<Continue>'
                break

            critic_feedback = self.step_critic(
                software_name=software_name,
                tips=tips,
                main_goal=main_goal,
                current_task_text=current_task_text,
                finished_tasks=finished_tasks,
                next_task=next_task,
                screenshot_path=new_screenshot_path,
                if_screenshot=if_screenshot
            )

            if '<Continue>' in critic_feedback:
                stepcheck_decision = '<Continue>'
            elif '<Modify>' in critic_feedback:
                current_task_text = self.extract_task(critic_feedback, 'Modify')
                current_task.name = current_task_text
                stepcheck_decision = '<Continue>'
            elif '<Finished>' in critic_feedback:
                stepcheck_decision = '<Finished>'
            elif '#Cannot confirm' in critic_feedback and iter_idx < 2:
                
                if parsed_screenshot:
                    compress_gui = self.compress_and_format_gui(parsed_screenshot)
                    new_screenshot_path = run_locateregion(
                        LMM=self.lmm,
                        software_name=software_name,
                        current_task=current_task_text,
                        gui_info=compress_gui,
                        screenshot_path=screenshot_path)
                else: # for claude computer use that has the actor ability
                    pass

                stepcheck_decision = '<Retry>' # current do nothing
            elif '<Pass>' in critic_feedback:
                stepcheck_decision = '<Finished>'
            else:
                stepcheck_decision = '<Continue>'


            iter_idx += 1
        
        return stepcheck_decision, current_task, history

    @staticmethod
    def extract_task(result, label):
        match = re.search(r'<%s>(.*?)</%s>'%(label, label), result, re.DOTALL)

        if match:
            extracted_text = match.group(1).strip()

            new_txt = ''
            for line in extracted_text.split("\n"):
                if not line.startswith('#'):
                    new_txt += line.strip()
            extracted_text = new_txt
        else:
            extracted_text = ''
        return extracted_text

    def subtask_refiner(self, software_name, tips, current_task, screenshot_path=None, if_screenshot=True):
        current_task = current_task.replace('[', '').replace(']', '')

        text_prompt =  f'''You are very smart, I would like your assistance for Desktop GUI automation.

I will provide the software name, a screenshot of the current environment, and task details.

You should help me refine the the task description of current task based on the given software tips and screenshot.

Software name: {software_name}
Software tips: {tips}

Information about Task:
{current_task}

The output format should be:

<Refine>
...
</Refine>

Note:
1) If no refinement of the task description is needed, please output with the original content.
2) Ensure the task description of the current task is clear and accurate, with no misunderstandings or redundant information.
3) If you did not receive the screenshot, please say it.

# Remember to reason in comment if needed.
'''
        prompt = [text_prompt, screenshot_path] if if_screenshot else [text_prompt] 
        
        result = run_lmm(
            prompt,
            lmm=self.lmm,
            max_tokens=1000, 
            temperature=0
        )

        match = re.search(r'<Refine>(.*?)</Refine>', result, re.DOTALL)

        if match:
            extracted_text = match.group(1).strip()
        else:
            extracted_text = ''

        extracted_text = f"{extracted_text}"

        return extracted_text
    
    def step_critic(self, software_name, tips, main_goal, current_task_text, finished_tasks, next_task, screenshot_path, if_screenshot):

        prompt = self.construct_step_critic_prompt(
            software_name,
            tips,
            main_goal,
            current_task_text,
            finished_tasks,
            next_task,
            screenshot_path,
            if_screenshot
        )

        critic_feedback = run_lmm(
            prompt,
            lmm=self.lmm,
            max_tokens=500, 
            temperature=0
        )

        return critic_feedback

    def construct_step_critic_prompt(self, 
        software_name,
        tips,
        main_goal,
        current_task,
        finished_tasks,
        next_task,
        screenshot_path=None,
        if_screenshot=True
    ):

        """Construct the detailed prompt for the LMM based on provided parameters."""
        text_prompt = f'''You are very smart, I would like your assistance for Desktop GUI automation.

I will provide the software name, a screenshot of the current environment, and task details.

You need to verify, based on the screenshot, whether the current task has been completed.

If already completed, please output <Finished> and reasons. Please be cautious to output <Finished>.

If require modification, please either add more plans or modify current step.

If you modify the current task, the output format should be as follows:

<Modify>
...
</modify>

If you think current task is unnecessary when you see the privided screenshot and the next task, please output:
<Pass>

For example, when current screenshot already includes the information can be used to solve next task, we may jump up current task, output <Pass>

If no change, the output format should be as follows:
<Continue>

Information about Task:
{main_goal}
{finished_tasks}
{current_task}
{next_task}

Software name: {software_name}
Software tips: {tips}

If you think current screenshot is not give all information to check the current task completion, please output '#Cannot confirm', we will provide a new screenshot.

Note:
1) Be very careful with the output <Finished>.
2) You have to carefully read the software tips to give your answer.
3) When you consider if the current task is necessary, please consider the content of next task.
4) When determine whether the button is clicked, please be careful to output <Finished>.


# Remember to reason in comment if needed.
'''

        return [text_prompt, screenshot_path] if if_screenshot else [text_prompt]        

    def compress_and_format_gui(self, gui):
        """Compress and format the GUI details for display."""
        compressed_gui = compress_gui(copy.deepcopy(gui))
        return "\n".join(format_gui(compressed_gui))

    def get_task_details(self, current_task, history):
        """Extract task name and main goal from current task."""
        if isinstance(current_task, str):
            return "", "", f"Current Task: {current_task}", ""
        
        main_goal = f"Main Goal: {current_task.parent.name}"
        
        summarized_history = self.get_code_history_for_current_task(history)
        finished_task = '\n'.join(summarized_history['finished_tasks'])
        finished_task = f"Previous Finished Tasks: {finished_task}"
        
        next_task = current_task.next().name if current_task.next() else "No more tasks"
        next_task = f"Next Task (for reference, you should consider whether current task is necessary when we complete next task ): {next_task}"
                
        current_task_text = f"Current Task: {current_task.name}"
        
        return main_goal, finished_task, current_task_text, next_task

    @staticmethod
    def check_resume(history):
        if history:
            history_code = "\n".join(history[-1]['code']) if history[-1]['code'][0] else "# finish"
            if "# finish" in history_code:
                return False
            else:
                return True
        else:
            "# finish"
        

    def get_code_history_for_current_task(self, history):
        # keep previous four steps
        finished_tasks, code = "", ""
        if history:
            if self.check_resume(history):
                # select self.history from -5 index to -1 index, needs to check length
                finished_tasks = [x['task'] for x in history[-5:-1]]
                code = "\n".join(history[-1]['code'])
            else:
                finished_tasks = [x['task'] for x in history[-4:]]
        return {"finished_tasks": finished_tasks, "code": code}
    
    def load_software_tips(self, resourcedir="resources\software_tips"):
        software_tips_files = glob.glob(os.path.join(os.path.dirname(__file__), resourcedir, "*.json"))

        # load files and merge them
        software_tips = {}
        for file in software_tips_files:
            with open(file, 'r') as f:
                software_tips.update(json.load(f))
                
        return software_tips
        
    def get_software_tips(self, target, software_name):        
        hints = "\n".join(target.get(software_name, [""]))
        return hints
    