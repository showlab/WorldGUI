import os
import sys
import json
from flask import Flask, request, jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from agent.config import basic_config
from agent.planner_critic.task_manager import decode_task
from agent.actor_critic.actorcritic import ActorCritic
from agent.utils.server_utils import generate_task_id, setup_directories, save_request_data, save_screenshot_multiple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
BASE_DIR = "actorcritic"
CACHE_DIR = os.path.join(basic_config['os_agent_settings']['cache_dir'], BASE_DIR)
os.makedirs(CACHE_DIR, exist_ok=True)
PORT = basic_config['actorcritic']['port']
LMM = basic_config['actorcritic']['lmm']
CRITIC_LMM = basic_config['actorcritic']['critic_lmm']

# Initialize Flask and dependencies
app = Flask(__name__)
actor_critic = ActorCritic(lmm=LMM, critic_lmm=CRITIC_LMM)

@app.route('/api/actorcritic', methods=['POST'])
def handle_command():
    data = request.json
    
    task_id = data.get('task_id', generate_task_id())
    step_id = data.get('step_id', 0)
    
    # Setup directories for saving request and response data
    request_dir, response_dir = setup_directories(CACHE_DIR, task_id)
    
    # Save request data
    save_request_data(data, request_dir, step_id)
    screenshot_path = save_screenshot_multiple(data, request_dir, step_id)

    code, state = actor_critic(
        current_task=decode_task(data.get('current_task')),
        current_action=data.get('current_action'),
        parsed_screenshot=data.get('parsed_screenshot', None),
        screenshot_path=screenshot_path,
        history=data.get('history'),
        software_name=data.get('software_name')
    )

    result = {'step': step_id,
            'code': code, 
            'state': state}

    # Save response data
    with open(os.path.join(response_dir, f'actioncritic-{step_id}.json'), 'w') as f:
        json.dump(result, f, indent=4)
        print(f"Saved result to {os.path.join(response_dir, f'action-{step_id}.json')}")

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False, port=PORT)
