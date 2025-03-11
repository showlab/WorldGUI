import os
import re
import sys
import io
import copy
import json
import glob
from agent.actor.utils import format_gui, compress_gui
from agent.utils.lmm.run_lmm import run_lmm


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class ActorCritic:
    """Tool that critic the task completion"""

    name = "ActorCritic"
    description = (
        '''
This tool can critiquing the completion of the current task.
''')

    def __init__(self, lmm="gpt-4o-2024-08-06", critic_lmm="gpt-4o-2024-08-06"):
        super(ActorCritic, self).__init__()
        self.lmm = lmm
        self.critic_lmm = critic_lmm

        self.critic_software_tips = self.load_software_tips("resources\critic_software_tips")
        self.software_tips = self.load_software_tips()
        

    def __call__(self,
                current_task,
                current_action,
                parsed_screenshot,
                screenshot_path=None,
                history=None,
                software_name=None,
                **kwargs):
        """
        Parameters:
            current_task: The current task to be processed.
            gui: Current state of the GUI.
            input_image: An optional screenshot used for updating GUI state.
            history: A list tracking the history of executed tasks and interactions.
            software_name: The name of the software being interacted with.
            **kwargs: Additional keyword arguments.

        Returns:
            A tuple containing the interaction code, updated current task, updated history, and a status message.
        """

        # prepare the information for constructing the prompt  
        # Task Info
        main_goal, finished_tasks, current_task_text, next_task = self.get_task_details(current_task, history)
        
        # GUI Info
        if parsed_screenshot is not None:
            compressed_gui = self.compress_and_format_gui(parsed_screenshot)
        else:
            compressed_gui = ""

        # software tips
        critic_tips = self.get_software_tips(self.critic_software_tips, software_name.lower())
        tips = self.get_software_tips(self.software_tips, software_name.lower())

        critic_prompt = self.construct_critic_prompt(software_name, current_task_text, current_action, compressed_gui, critic_tips, screenshot_path)

        # Prepare the action code based on the current task.
        success_flag, reason, critic_comment = self.generate_critic(prompt=critic_prompt, lmm=self.critic_lmm)


        if success_flag.lower() == 'false':
            
            ## locate the gui info

            if compress_gui:
                reffered_gui = self.locate_gui_info(compressed_gui, main_goal, current_task_text)
            else:
                reffered_gui = ""

            if current_action != None:
                current_action = self.extract_purecode(current_action) # only pure code, no reasoning description
            else:
                current_action = ""

            correction_prompt = self.construct_correction_prompt(
                current_action, 
                critic_comment, 
                reffered_gui, 
                main_goal,
                current_task_text,
                tips,
                screenshot_path=None) # no screenshot provided
            code = self.generate_correction(correction_prompt)
            return self.extract_code(code), "<Critic>"
        else:
            return "", '<Next>'
    

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
        next_task = f"Next Task (for reference, you only need to complete the current task): {next_task}"
                
        current_task_text = f"Current Task: {current_task.name}"
        
        return main_goal, finished_task, current_task_text, next_task

    def get_api_details(self):
        """Format API details for the prompt."""
        return f'the pyautogui API imported\n{self.available_api_illustration}'

    def locate_gui_info(self, gui_info, main_goal, current_task):

        text_prompt =  f'''
By examinig the gui screenshot information, select all related coordinates which needed to complete the current task.
Parsed GUI Screenshot Info: [Note that: element format is "name [its position]", separate with comma]
{gui_info}

Information about Task:
{main_goal}
{current_task}

Note:
1) You have to go through all the element of give GUI screenshot info.
2) If there are multiple elements in GUI screenshot info, please output the coordinates for all of them.
3) If there repeat elements in GUI screenshot info, please output the coordinates for all of them.
4) The output format should be "name [its position]".

The output format should be:
```plaintext
...
```

# Remember to reason in comment if needed.
'''
        referred_gui = run_lmm(text_prompt, lmm=self.lmm, max_tokens=1000, temperature=0)

        referred_gui = self.extract_refer_gui(referred_gui)

        return referred_gui

    def construct_critic_prompt(self, 
        software_name, 
        current_task, 
        current_action, 
        gui_info,
        tips, 
        screenshot_path=None):
        """Construct the detailed prompt for the LMM based on provided parameters."""
        
        text_prompt =  f'''Based on the screenshots before and after the action, subtask description, software name {software_name}, please check the action completion status.
{current_task}
current action: {current_action}

Parsed GUI Screenshot Info: [Note that: element format is "name [its position]", separate with comma]
{gui_info}

The output format:
```plaintext
<Success> bool (Current task completion status) </Success>
<Reason> str (Analysis of possible mistakes if action is wrong) </Reason>
```

Software Usage Tips:
{tips}

Note:
1) Please carefully review the screenshot. Use it to verify whether the current task has been successfully completed.
2) Please based on the screenshot provided to give the potential reason of unsuccessful action.
3) When notice the pop-up window, that means the task is incomplete. Please do not output true for <Success> flag.
4) When determine the task completion status, please consider the current action which is already executed in the environment.

Please provide the reasoning steps.
'''
        
        if screenshot_path is not None:
            if len(screenshot_path) == 2:
                if screenshot_path[0] != "":
                    prompt = [text_prompt, screenshot_path[0], screenshot_path[1]]
                else:
                    prompt = [text_prompt, screenshot_path[1]]
            else:
                prompt = [text_prompt, screenshot_path[0]]
        else:
            prompt = [text_prompt]

        return prompt

    def generate_critic(self, prompt, lmm):
        """Run the LMM to generate code based on the prompt and post-process it."""

        critic_results = run_lmm(
            prompt,
            lmm=lmm,
            max_tokens=1000, 
            temperature=0
            )

        success_flag, reason = None, None

        success_flag = self.extract_patterntext(critic_results, 'Success')
        reason = self.extract_patterntext(critic_results, 'Reason')
        critic_comment = ""


        if success_flag == None or reason == None:
            return "false", "false", "", critic_comment

        if success_flag.lower() == 'false':
            critic_comment = reason
        
        return success_flag, reason, critic_comment

    def construct_correction_prompt(
        self,
        current_action,
        critic_comment,
        referred_gui,
        main_goal,
        current_task,
        tips,
        screenshot_path=None
    ):
        text_prompt =  f'''Please, based on the parsed GUI elements of the screenshot below, use pyautogui and the following API to generate execution code to control the mouse and keyboard. Additionally, provide a natural language suggestion to explain your reasoning and actions taken.
Currently, we execute the code: {current_action}, 
but we obtain this feedback: {critic_comment}.
You should based on above feedback regenerate the execution code.

Parsed GUI Screenshot Info: [Note that: element format is "name [its position]", separate with comma]

Based on the task description, we extarct the corresponding coordinates from GUI screenshot like that: {referred_gui}


Information about Task:
{main_goal}
{current_task}


General Rules:
1. Don't write an algorithm to search on the GUI data, directly fill the coordinates in the corresponding API.
2. MUST REMEMBER all the parameters in the function should be filled with the specific constant, not the variable.
3. IMPORTANT: Sometimes you need to do some reasoning or calculation for the position. You MUST do it in the comment of the code. 
4. Follow exactly the instructions in the task description. Don't redo tasks in finished_tasks.
5. For navigation-related tasks on a page or document, follow these steps to do the reasoning. Provide reasoning steps in the comments: 
    1) Check if the required information is displayed on the screenshot. MUST Answer this question in the comment of the code.
    2) If info is NOT found, use `press('pagedown')` one time to scroll down.

Software Usage Tips:
{tips}

==============================
Now, complete the code to achieve the command and generate a natural language suggestion of the reasoning steps. The explanation should be concise, logical, and easy to follow. Ensure that the explanation addresses why you did what you did, any necessary adjustments, and potential issues you considered.
Output format:
```output
<Code>
from pyautogui import click, write, hotkey, press, scroll, keyDown, keyUp, doubleClick
# Don't import any other libraries and functions
# Remember to reason in comment if needed.
# You must output 'from pyautogui import click, write, hotkey, press, scroll, keyDown, keyUp, doubleClick' if needed.
</Code> 
<Suggestion>
str(Explain how to fix the previous mistake based on the feedback. Provide a concise, step-by-step explanation of what needs to be done to execute correctly.)
</Suggestion> 
```
'''
        return [text_prompt, screenshot_path] if screenshot_path is not None else [text_prompt]

    def generate_correction(self, prompt):
        correction_results = run_lmm(
            prompt, 
            lmm=self.lmm,
            max_tokens=1000, 
            temperature=0
            )
        
        return correction_results

    def post_process_code(self, code):
        """Post-process the generated code to adapt to standards and replace API calls."""
        processed_code = []
        for line in code.split("\n"):
            if not line.strip().startswith("#"):
                for api in self.available_api.values():
                    if api.name in line:
                        line = line.replace(api.name, f"self.available_api['{api.name}']")
                        line = eval(line)  # Potential security risk, consider safer alternatives
            processed_code.append(line)
        return "\n".join(processed_code)

    @staticmethod
    def extract_patterntext(result, label):
        match = re.search(r'<%s>(.*?)</%s>'%(label, label), result, re.DOTALL)

        if match:
            extracted_text = match.group(1).strip()

            new_txt = ''
            for line in extracted_text.split("\n"):
                if not line.startswith('#'):
                    new_txt += line.strip()
            extracted_text = new_txt
        else:
            extracted_text = None
        return extracted_text

    @staticmethod
    def extract_code(input_string):
        # Regular expression to extract content starting from '<Code>' until the end if there are no closing backticks
        pattern = r'<Code>(.*?)</Code>'
        
        # Extract content
        matches = re.findall(pattern, input_string, re.DOTALL)  # re.DOTALL allows '.' to match newlines as well
        
        # Return the first match if exists, trimming whitespace and ignoring potential closing backticks
        return matches[0].strip() if matches else ""
    
    @staticmethod
    def extract_purecode(code):
        """Post-process the generated code to adapt to standards and replace API calls."""
        processed_code = []
        for line in code.split("\n"):
            if not line.strip().startswith("#"):
                processed_code.append(line)
        return "\n".join(processed_code)

    @staticmethod
    def extract_refer_gui(input_string):
        # Regular expression to extract content starting from '```plaintext' until the end if there are no closing backticks
        pattern = r'```plaintext(.*?)```'
        
        # Extract content
        matches = re.search(pattern, input_string, re.DOTALL)  # re.DOTALL allows '.' to match newlines as well
        
        # Return the first match if exists, trimming whitespace and ignoring potential closing backticks
        return matches.group(1).strip() if matches else input_string

    @staticmethod
    def check_resume(history):
        history_code = "\n".join(history[-1]['code']) if history else "# finish"
        if "# finish" in history_code:
            return False
        else:
            return True

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

    def get_last_screenshot(self, history):
        return history[-1]['screenshot_path'][-1], history[-1]['gui'][-1]
    
    def get_last_code(self, history):
        return history[-1]['code'][-1]
    
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
    
    
