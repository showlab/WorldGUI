import requests
from agent.utils.lmm.lmm_utils import encode_image

def send_gui_parser_request(url, software_name, screenshot_path, meta_data, task_id=None, step_id=None):
    """Send a POST request to the server with the query and the image."""
    # Encode the image
    screenshot_data = encode_image(screenshot_path)
    
    # Construct the request data
    data = {
        "screenshot": screenshot_data,
        "GUI": meta_data,
        "software_name": software_name,
        "task_id": task_id,
        "step_id": step_id
    }
    
    # Send POST request
    response = requests.post(url, json=data)
    return response.json()