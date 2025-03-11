import os
import sys
import openai

from flask import Flask, request, jsonify
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from agent.config import basic_config
from agent.gui_parser.gui_parser import GUIParser
from agent.utils.server_utils import generate_task_id, setup_directories, save_request_data, save_screenshot, find_non_serializable

import logging
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config', 'googleocr-config.json'))
openai.api_key = os.getenv('OPENAI_KEY')


# Initialize Flask application
app = Flask(__name__)

# Define directories for images and cache
BASE_DIR = "gui_parser"
CACHE_DIR = os.path.join(basic_config['os_agent_settings']['cache_dir'], BASE_DIR)
os.makedirs(CACHE_DIR, exist_ok=True)
PORT = basic_config['gui_parser']['port']

@app.route('/api/gui_parser', methods=['POST'])
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
    
    # Create an instance of LLMActor and call it with all parameters
    gui_parser = GUIParser(cache_folder=os.path.join(CACHE_DIR, task_id))
    result = gui_parser(
        meta_data=data['GUI'],
        screenshot_path=screenshot_path,
        software_name=data['software_name']
    )
    
    print("Result:", result)
    # Save result in pickle format
    # save_result(result, response_dir, step_id)
    import pickle
    with open(os.path.join(response_dir, f'parsed_gui-{step_id}.pkl'), 'wb') as f:
        pickle.dump(result, f)
        print(f"Saved result to {os.path.join(response_dir, f'parsed_gui-{step_id}.pkl')}")
        
    find_non_serializable(result)
    
    with open(os.path.join(response_dir, f'parsed_gui-{step_id}.json'), 'w') as f:
        json.dump(result, f, indent=4)
        print(f"Saved result to {os.path.join(response_dir, f'parsed_gui-{step_id}.json')}")
            
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=PORT)
