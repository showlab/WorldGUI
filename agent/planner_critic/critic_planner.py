import os
import json
import re
import copy
import glob

from moviepy.editor import VideoFileClip
import whisper

# os.sys.path.append("../")
from agent.utils.lmm.run_lmm import run_lmm
from agent.gui_parser.sender import send_gui_parser_request
from agent.actor.utils import format_gui, compress_gui


class CriticPlanner():
    name = "CriticPlanner"
    description = (
        '''Can transfer an query into detailed steps with screenshot information and critic feedback'''
    )

    def __init__(self, lmm="gpt-4o-2024-08-06", lmm_critic="gpt-4o-2024-08-06"):
        super(CriticPlanner, self).__init__()
        self.lmm = lmm
        self.lmm_critic = lmm_critic

        self.software_tips = self.load_software_tips()

    def save_audio(self, video_path, audio):
        audio_path = video_path.replace(".mp4", ".mp3")
        if not os.path.exists(audio_path):
            audio.write_audiofile(audio_path)
        return audio_path

    def subtitle_to_text(self, input_data):
        output = ""
        for entry in input_data:
            output += f"{entry['start']:.2f} - {entry['end']:.2f}\n{entry['text'].strip()}\n"
        return output

    def extract_plan(self, input_string):
        # Regular expression to extract content from '```plan ... ```'
        pattern = r'```plan(.*?)```'
        # Extract content
        matches = re.findall(pattern, input_string, re.DOTALL)  # re.DOTALL allows '.' to match newlines as well
        # Return the first match if exists, else original
        return matches[0].strip() if matches else input_string

    def parse_savedplans(self, plan_path, steps):
        savefile = open(plan_path, "w", encoding="utf-8")
        
        for txt in steps.split('\n'):
            filtered_txt = txt.replace("\"", "'")
            if filtered_txt.startswith("\""):
                filtered_txt = filtered_txt[1:]
            if txt.endswith("\""):
                filtered_txt = filtered_txt[:-1]
            
            filtered_txt = filtered_txt.strip()
            savefile.write(filtered_txt+'\n')
        
        savefile.close()

    def parse_correctedplans(self, critic_results):
        str_idx = critic_results.find('<Flag>')
        end_idx = critic_results.find('</Flag>')
        flag_re = critic_results[(str_idx+len('<Flag>')):end_idx].strip().lower()

        if flag_re == 'false':
            str_idx = critic_results.find('<Correction>')
            end_idx = critic_results.find('</Correction>')
            corrected_plans = critic_results[(str_idx+len('<Correction>')):end_idx]

            corrected_plans = corrected_plans.replace("\n-",'.')
            
            temp_plans = []
            for line in corrected_plans.split('\n'):
                temp_plans.append(line.replace('-', '').strip())
            corrected_plans = '\n'.join(temp_plans)
        else:
            corrected_plans = None

        return corrected_plans

    def getsubtitle(self, video_path, subtitle_path):
        if os.path.exists(subtitle_path):
            subtitle = json.load(open(subtitle_path, "r"))
        elif os.path.exists(video_path):
            video = VideoFileClip(video_path)
            audio = video.audio
            audio_path = self.save_audio(video_path, audio)
            asr_model = whisper.load_model("base")
            subtitle = self.subtitle_to_text(asr_model.transcribe(audio_path)['segments'])

            with open(subtitle_path, "w") as f:
                json.dump(subtitle, f)
        else:
            subtitle = ""
            
        return subtitle

    def getrawsteps(self, software, video_name, video_path, subtitle):

        text_prompt = f'''{subtitle}
        
The text above is the subtitle from an instructional video about {software}, titled "{video_name}". 
Its format includes one line for the time span and one line for the narration.

Please extract the procedure (only the procedure, omitting unrelated parts) to achieve the desired goal, and format it as follows:
```plan
Task 1: Create a new composition
Subtask 1: Click the 'New Composition' button
Subtask 2: ...
Task 2: ...
```

Note:
1. The subtitle was extracted by a model, so it may contain errors. Please correct them while outputting the content.
2. If the video does not provide specific steps, use your knowledge to fill in the gaps.

Let's begin:'''

        raw_plan_path = os.path.join(os.path.dirname(video_path), f"{self.lmm}", os.path.basename(video_path).replace(".mp4", f"-raw-plan.json"))

        saved_dirpath = os.path.dirname(raw_plan_path)
        if not os.path.exists(saved_dirpath):
            os.makedirs(saved_dirpath)

        if os.path.exists(raw_plan_path):
            raw_steps = json.load(open(raw_plan_path, "r"))
        else:
            raw_steps = run_lmm([text_prompt], lmm=self.lmm, max_tokens=1000, temperature=0)
            raw_steps = self.extract_plan(raw_steps)
            json.dump(raw_steps, open(raw_plan_path, "w", encoding="utf-8"), ensure_ascii=False)
        
        return raw_steps

    def getrefinedplans(self, software, query, video_name, video_path, raw_steps, screenshot_path):

        text_prompt = f'''The user is currently utilizing {software}. 
Please modify or delete unnecessary steps according to the user's unique requirements: 
Modifications could include:
1) Delete unnecessary parts. for example, remove the importing footage step if the user's video has already been added to the track.
2) Change the content. For example, the video is about achieving an effect on the text "hello", but the user wants to generate "world".
3) Remove any unnecessary steps based on the information provided in the screenshot image.

The screenshot shows the current software state. Based on the screenshot, you have to remove unnecessary steps.
For example, the text 'hello world' already selected, remove the step 'select the text hello world in the first slide.'.

Steps in Instructional Video with title {video_name}:
{raw_steps}

User Query: {query}

Output format: 
```plan
Task 1: ...
Subtask 1: ...
Subtask 2: ...
Task 2: ...
```
# Remember to reason in comment if needed.

Note that: 
1) The project file is already opened, no need to open it again.
2) In your subtask, you must specify which button to click, and which footage to manipulate, according to a user query.
3) Omit all video viewing process.
4) Omit all actions like identify.
5) The action types in Subtask should be in [Click/DoubleClick/RightClick, Scroll, Drag, Type, Write, Press] 
6) Avoid generate navigation or location actions, as they don't align with any specified step above; directly click on the desired link instead. 

Refined steps:'''

        if len(query) > 200:
            query = query[:200]

        refined_steps = run_lmm([text_prompt, screenshot_path], lmm=self.lmm, max_tokens=1000, temperature=0)
        refined_steps = self.extract_plan(refined_steps)
        
        # format plan
        refined_steps = refined_steps.replace('\n-', '-')

        return refined_steps

    def getplans_novideo(self, software, query, screenshot_path):

        text_prompt = f'''The user is currently utilizing {software}. The screenshot shows the current software state. You need to based on the provided screenshot and the following user query to give a plan for control the mouse and keyboard to complete a computer use task.

User Query: {query}

Output format: 
```plan
Task 1: ...
Subtask 1: ...
Subtask 2: ...
Task 2: ...
```
# Remember to reason in comment if needed.

Note that: 
1) The project file is already opened, no need to open it again.
2) In your subtask, you must specify which button to click, and which footage to manipulate, according to a user query.
3) Omit all video viewing process.
4) Omit all actions like identify.
5) The action types in Subtask should be in [Click/DoubleClick/RightClick, Scroll, Drag, Type, Write, Press] 
6) Avoid generate navigation or location actions, as they don't align with any specified step above; directly click on the desired link instead. 

Refined steps:'''


        if len(query) > 200:
            query = query[:200]

        plans = run_lmm([text_prompt, screenshot_path], lmm=self.lmm, max_tokens=1000, temperature=0)
        plans = self.extract_plan(plans)
        
        # format plan
        plans = plans.replace('\n-', '-')

        return plans


    def get_gui_information(self, url, software, screenshot_path, meta_data, ProjectID):
        gui_results = send_gui_parser_request(url, software, screenshot_path, meta_data, task_id=ProjectID, step_id=0)
        compressed_gui = compress_gui(copy.deepcopy(gui_results))
        compressed_gui = "\n".join(format_gui(compressed_gui))

        return compressed_gui

    def plancritic(self, software, video_name, query, plans, compressed_gui, screenshot_path, raw_steps, tips):

        visual_prompt = "screenshot image" if compressed_gui is None else "screenshot image and the parsed GUI screenshot"

        text_prompt =  f'''You are very smart, I would like your assistance for Desktop GUI automation.

I will provide the software name, key steps from the instructional video, the user query, and the initial plans.

You need to verify whether the provided initial plans can fulfill the user query. If not, please revise the plans. 

Software name: {software}
Software tips: {tips}

Extracted key steps of instruction video {video_name}: {raw_steps}

User Query: {query}

Plans ready for evaluation: {plans}

I will provide the {visual_prompt} to represent the current Desktop GUI state about {software}.
Parsed GUI Screenshot Info: [Note that: element format is "name [its position]", separate with comma]
{compressed_gui}


The output format is as follows:

<Finish></Finish>\n<Feedback></Feedback>\n<Flag>\n<Correction></Correction>\n<Reason></Reason>

<Flag>: should be set to either true or false. If the plans are correct, selecting true, else selecting false.
<Feedback>: If the plan is correct, please explain why. If the plan is incorrect selecting one of the following error types: 'Wrong steps', 'Missing steps', or 'Redundant steps'. Please provide the reasoning steps when giving the feedback.
If the error type is 'wrong steps', please specify the exact steps that are incorrect. 
If the error type is 'Missing Steps', please identify the specific steps that are missing.
If the error type is 'Redundant steps', please point out the steps that are unnecessary.

<Correction>: If the plans are correct or the task is finished, output 'None', else output the corrected plans.
The format it as follows:
<Correction>
Task 1: Create a new composition
Subtask 1: Click the 'New Composition' button
Subtask 2: ...
Task 2: ...
</Correction>

<Reason>Please give your reason...</Reason>

Note:
1) Check whether the current state, as shown in the provided screenshot, fulfills the user query.
2) If not complete, please verify whether the provided plans can fulfill the user query. Note that the plans will be executed based on the current state shown in the screenshot, so you need to check if any steps in the plans are redundant, missing or wrong.
3) Please review each step of the plan to ensure its correctness.
4) The key steps we extracted from the instruction video can be seen the external knowledge for you to critic our plans.
5) The project file is already opened, no need to open it again.


# Remember to reason in comment if needed.
'''

        critic_results = run_lmm([text_prompt, screenshot_path], lmm=self.lmm_critic, max_tokens=1000, temperature=0)

        corrected_plans = self.parse_correctedplans(critic_results)

        if corrected_plans is not None:
            return corrected_plans
        else:
            return plans

    def __call__(self, query, software, video_path, screenshot_path, gui_info):

        if video_path:
            video_name = os.path.basename(video_path)
            subtitle_path = video_path.replace(".mp4", ".json")

            subtitle = self.getsubtitle(video_path, subtitle_path)

            if subtitle != "":
                raw_steps = self.getrawsteps(software, video_name, video_path, subtitle)
            else:
                raw_steps = ""

            init_plans = self.getrefinedplans(software, query, video_name, video_path, raw_steps, screenshot_path)

            tips = self.get_software_tips(self.software_tips, software.replace(' ', '').lower())
            plans = self.plancritic(software, video_name, query, init_plans, gui_info, screenshot_path, raw_steps, tips)
        else:

            init_plans = self.getplans_novideo(software, query, screenshot_path)

            tips = self.get_software_tips(self.software_tips, software.replace(' ', '').lower())

            plans = self.plancritic(software, "", query, init_plans, gui_info, screenshot_path, "", tips)

        return plans
        
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