import os
import sys
import json

from flask import Flask, request, jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from agent.config import basic_config
from agent.planner_critic.task_manager import encode_task, decode_task
from agent.step_check.stepcheck import StepCheck
from agent.utils.server_utils import generate_task_id, setup_directories, save_request_data, save_screenshot
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
BASE_DIR = "step_check"
CACHE_DIR = os.path.join(basic_config['os_agent_settings']['cache_dir'], BASE_DIR)
os.makedirs(CACHE_DIR, exist_ok=True)
PORT = basic_config['step_check']['port']
LMM = basic_config['step_check']['lmm']

# Initialize Flask and dependencies
app = Flask(__name__)
stepcheck = StepCheck(lmm=LMM)

@app.route('/api/step_check', methods=['POST'])
def handle_command():
    data = request.json
    
    task_id = data.get('task_id', generate_task_id())
    step_id = data.get('step_id', 0)
    
    # Setup directories for saving request and response data
    request_dir, response_dir = setup_directories(CACHE_DIR, task_id)

    # Save request data
    save_request_data(data, request_dir, step_id)
    screenshot_path = save_screenshot(data, request_dir, step_id)

    print(decode_task(data.get('current_task')))

    stepcheck_decision, current_task, history = stepcheck(
        current_task=decode_task(data.get('current_task')),
        parsed_screenshot=data.get('parsed_screenshot', {}),
        screenshot_path=screenshot_path,
        stepcheck_decision=data.get('stepcheck_decision'),
        history=data.get('history'),
        software_name=data.get('software_name'),
        if_screenshot=data.get('if_screenshot')
    )

    result = {'step': step_id,
            'stepcheck_decision': stepcheck_decision, 
            'current_task': encode_task(current_task), 
            'history': history}

    with open(os.path.join(response_dir, f'stepcheck-{step_id}.json'), 'w') as f:
        json.dump(result, f, indent=4)
        print(f"Saved result to {os.path.join(response_dir, f'stepcheck-{step_id}.json')}")

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False, port=PORT)
