import os
import sys
import json
import logging
from flask import Flask, request, jsonify
import openai

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from agent.config import basic_config
from agent.planner_critic.critic_planner import CriticPlanner
from agent.utils.server_utils import generate_task_id, setup_directories, save_request_data, save_screenshot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Initialize Flask application
app = Flask(__name__)

# Define directories for images and cache
BASE_DIR = "planner_critic"
CACHE_DIR = os.path.join(basic_config['os_agent_settings']['cache_dir'], BASE_DIR)
os.makedirs(CACHE_DIR, exist_ok=True)
PORT = basic_config['planner_critic']['port']

planner = CriticPlanner(lmm=basic_config['planner_critic']['lmm'], lmm_critic=basic_config['planner_critic']['lmm_critic'])

@app.route('/api/planner_critic', methods=['POST'])
def handle_command():
    # Get JSON data
    data = request.json
    
    task_id = data.get('task_id', generate_task_id())
    step_id = data.get('step_id', 0)
    
    # Setup directories for saving request and response data
    request_dir, response_dir = setup_directories(CACHE_DIR, task_id)
    
    # Save request data
    save_request_data(data, request_dir, step_id)
    screenshot_path = save_screenshot(data, request_dir, step_id)
   
    result = planner(
        query=data['query'],
        software=data['software_name'],
        video_path=data['video_path'], 
        screenshot_path=screenshot_path,
        gui_info=data['gui_info']
    )
    
    with open(os.path.join(response_dir, f'plan.json'), 'w') as f:
        json.dump(result, f, indent=4)
        print(f"Saved result to {os.path.join(response_dir, f'plan.json')}")

    # Return the results
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=PORT)
