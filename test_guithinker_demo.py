import os
import copy
import time
import json
import glob
import shutil
import argparse

import subprocess

from agent.autopc import AutoPC
from agent.utils.gui_capture import get_screenshot, focus_software
from agent.gui_parser.sender import send_gui_parser_request
from agent.actor.utils import format_gui, compress_gui

from agent.config import basic_config

def main():
    parser = argparse.ArgumentParser(description="GUI-Thinker Locally Running")
    parser.add_argument("--software_name", type=str, default="PowerPoint")
    parser.add_argument("--taskID", type=int, default=1, help="index of tasks in the data json file.")
    parser.add_argument("--aug_id", type=int, default=0, help="index of augmentations. 0 represent no augmentation.")
    parser.add_argument("--data_path", type=str, default="./data/demo.json")
    parser.add_argument("--maximum_step", type=int, default=20, help="total steps")
    parser.add_argument("--max_critic_trials", type=int, default=3, help="set the maiximum trials of critic times")
    args = parser.parse_args()

    saved_folder = 'test_results/%s'%(basic_config['planner_critic']['lmm'])

    software_name = args.software_name
    aug_id = args.aug_id

    datafile = json.load(open(args.data_path,'r'))[args.taskID]

    video_path = datafile["video_path"]
    projectID = datafile['project_id']
    query = datafile['user_query']

    if software_name == "PowerPoint":
        projfile_path = os.path.join(os.path.dirname(video_path), "project.pptx")
    elif software_name == "Word":
        projfile_path = os.path.join(os.path.dirname(video_path), "project.docx")
    elif software_name == "Excel":
        projfile_path = os.path.join(os.path.dirname(video_path), "project.xlsx")
    else:
        projfile_path = ''

    ## load all aug files
    augfiles = glob.glob(os.path.join(os.path.dirname(video_path), 'aug*.json'))
    augfiles.insert(0, None)
    augfile = augfiles[aug_id]

    if augfile is not None:
        pre_actions = json.load(open(augfile, 'r'))

        subprocess.Popen([projfile_path], shell=True)
        time.sleep(2)
        exec(pre_actions)
    else:
        subprocess.Popen([projfile_path], shell=True)
        time.sleep(2)

    maximum_step = args.maximum_step
    max_critic_trials = args.max_critic_trials
    state = '<Continue>'
    code = ""
    last_screenshot_path = ""
    critic_count = 0

    autopc = AutoPC(software_name=software_name, project_id=projectID)

    # Focus current software and get the initial screenshot
    focus_software(software_name)
    meta_data, screenshot_path = get_screenshot(software_name)

    if augfile:
        aug_name = os.path.basename(augfile).split('.')[0]
        new_screenpath = os.path.join("%s"%(saved_folder), software_name, "%s_%s_start.png"%(projectID, aug_name))
    else:
        aug_name = "meta"
        new_screenpath = os.path.join("%s"%(saved_folder), software_name, "%s_start.png"%(projectID))

    print('Save result in', new_screenpath)
    os.makedirs(os.path.dirname(new_screenpath), exist_ok=True)
    shutil.copy(screenshot_path, new_screenpath)


    gui_results = send_gui_parser_request(basic_config['gui_parser']['url'], software_name, screenshot_path, meta_data, task_id=projectID, step_id="1")
    gui_info = compress_gui(copy.deepcopy(gui_results))
    gui_info = "\n".join(format_gui(gui_info))


    print('User Query:', query)

    focus_software(software_name)
    plan = autopc.run_planner(query, software_name, screenshot_path, gui_info, video_path)

    print('Plan:\n', plan)

    for idx in range(maximum_step):
        meta_data, screenshot_path = get_screenshot(software_name)
        
        print("===Current task===", "Index:",  idx, state)
        print(autopc.current_task.name.strip())
        code, state, current_task = autopc.run_step(state,
                                                    code,
                                                    autopc.current_task, 
                                                    meta_data, 
                                                    last_screenshot_path,
                                                    screenshot_path, 
                                                    software_name,
                                                    if_screenshot=True)
        
        ## execute the action code
        if code != "":
            focus_software(software_name)
            exec(code)
            last_screenshot_path = screenshot_path
        
        if state == '<Continue>':
            state = '<Critic>'

        elif state == '<Next>':
            autopc.current_task = autopc.current_task.next()
            if autopc.current_task:
                state = '<Continue>'
                code = ""
                critic_count = 0
            else:
                state = '<Finished>'
                print("===Current task===", "Index:",  idx, state)
                break
            
        
        if state == '<Critic>':
            critic_count += 1
        
        if critic_count > max_critic_trials:
            autopc.current_task = autopc.current_task.next()
            if autopc.current_task:
                state = '<Continue>'
                code = ""
                critic_count = 0
            else:
                state = '<Finished>'
                print('current index', idx, state)
                break

    if augfile:
        aug_name = os.path.basename(augfile).split('.')[0]
        new_screenpath = os.path.join("%s"%(saved_folder), software_name, "%s_%s_end.png"%(projectID, aug_name))
    else:
        new_screenpath = os.path.join("%s"%(saved_folder), software_name, "%s_end.png"%(projectID))
    print('Save result in', new_screenpath)
    os.makedirs(os.path.dirname(new_screenpath), exist_ok=True)
    shutil.copy(screenshot_path, new_screenpath)

if __name__ == "__main__":
    main()
