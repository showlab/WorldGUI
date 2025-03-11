import os
import re
import copy
import json
import glob
from agent.actor.utils import format_gui, compress_gui
from agent.utils.lmm.run_lmm import run_lmm

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class Actor:
    """Tool that adds the capability to locate image region with a natural language query."""

    name = "lmm_actor"
    description = (
        '''
This tool can translate the user's language commands into Python code that can operate the keyboard and mouse.
Invoke command: lmm_actor(query, visual[i])
:param query -> str, specific command. visual[i] -> image, the latest screenshot.
''')

    def __init__(self, lmm="gpt-4o-2024-08-06"):
        super(Actor, self).__init__()
        self.lmm =lmm
        self.software_tips = self.load_software_tips()
    def __call__(
        self,
        current_task,
        parsed_screenshot=None,
        screenshot_path=None,
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
            parsed_screenshot: parsed gui information.
            screenshot_path: str.
            history: A list tracking the history of executed tasks and interactions.
            software_name: The name of the software being interacted with.
            if_screenshot: bool.
            **kwargs: Additional keyword arguments.

        Returns:
            A tuple containing the interaction code, updated current task, updated history, and a status message.
        """

        code = self.query_to_action(
            parsed_screenshot=parsed_screenshot, 
            history=history,
            current_task=current_task,
            screenshot_path=screenshot_path,
            software_name=software_name,
            if_screenshot=if_screenshot
        )

        return code, current_task, history

    def query_to_action(
        self, 
        parsed_screenshot, 
        history, 
        current_task, 
        screenshot_path,
        software_name,
        if_screenshot
    ):

        """Translate query to executed code."""
        # prepare the information for constructing the prompt


        if parsed_screenshot is not None:
            # GUI Info
            compressed_gui = self.compress_and_format_gui(parsed_screenshot)
        else:
            compressed_gui = ""

        # Task Info
        main_goal, finished_tasks, current_task_text, next_task = self.get_task_details(current_task, history)
        
        # Software Usage Tips
        tips = self.get_software_tips(software_name.lower())
    

        # Run lmm to get code
        prompt = self.construct_prompt(
            gui_info=compressed_gui, 
            main_goal=main_goal, 
            finished_tasks=finished_tasks, # This is for provide some context for the current task
            current_task=current_task_text, 
            tips=tips, 
            screenshot_path=screenshot_path if screenshot_path else None,
            if_screenshot=if_screenshot
        )
            
        # Generate code with lmm
        code = self.generate_action(prompt)

        return code

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

    def construct_prompt(
        self, 
        gui_info, 
        main_goal, 
        finished_tasks, 
        current_task,
        tips, 
        screenshot_path,
        if_screenshot
    ):

        """Construct the detailed prompt for the LMM based on provided parameters."""
        visual_prompt = "" if screenshot_path is None else "screenshot image provided and"

        text_prompt =  f'''Please, based on {visual_prompt} the parsed GUI elements from the provided screenshot below, use pyautogui and the following API to control the computer's mouse and keyboard to complete the specified Current Task.
Parsed GUI Screenshot Info: [Note that: element format is "name [its position]", separate with comma]
{gui_info}

Information about Task:
{main_goal}
{finished_tasks}
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

Output format:
```output
<Code>
Now let's complete the code to achieve the command:
from pyautogui import click, write, hotkey, press, scroll, keyDown, keyUp, doubleClick
# Don't import any other libraries and functions
</Code>
<Reason>
Please give your reasoning steps...
</Reason>
```
'''

        return [text_prompt, screenshot_path] if if_screenshot else [text_prompt]

    def generate_action(self, prompt):
        """Run the lmm to generate code based on the prompt and post-process it."""

        code = run_lmm(
            prompt,
            lmm=self.lmm,
            max_tokens=1000, 
            temperature=0
        )
        
        code = self.extract_code(code)
        return code

    @staticmethod
    def extract_code(input_string):
        pattern = r'<Code>(.*?)</Code>'
        
        # Extract content
        matches = re.findall(pattern, input_string, re.DOTALL)  # re.DOTALL allows '.' to match newlines as well
        
        # Return the first match if exists, trimming whitespace and ignoring potential closing backticks
        return matches[0].strip() if matches else ""

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
    
    def load_software_tips(self, basedir=os.path.dirname(__file__)):
        software_tips_files = glob.glob(os.path.join(basedir, "resources\software_tips", "*.json"))

        # load files and merge them
        software_tips = {}
        for file in software_tips_files:
            with open(file, 'r') as f:
                software_tips.update(json.load(f))
                
        return software_tips
        
    def get_software_tips(self, software_name):        
        hints = "\n".join(self.software_tips.get(software_name, [""]))
        return hints
    
    
