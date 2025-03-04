import requests
from agent.utils.lmm.lmm_utils import encode_image
from agent.planner_critic.task_manager import encode_task, decode_task

def send_actor_request(
    url,
    current_task, 
    parsed_screenshot,
    screenshot_path: str, 
    software_name: str, 
    history: list=[], 
    task_id: str=None, 
    step_id: str=None,
    if_screenshot=True
):
    """Send a POST request to the server with the query and the image."""
    # Encode the image
    screenshot_data = encode_image(screenshot_path)
        
    # Construct the request data
    data = {
        "current_task": encode_task(current_task),
        "parsed_screenshot": parsed_screenshot,
        "screenshot": screenshot_data,
        "history": history,
        "software_name": software_name,
        "task_id": task_id,
        "step_id": step_id, 
        "if_screenshot": if_screenshot
    }
    
    # Send POST request
    response = requests.post(url, json=data)
    response = response.json()
    
    # Decode the current task
    response['current_task'] = decode_task(response['current_task'])

    return response