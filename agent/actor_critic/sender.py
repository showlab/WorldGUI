import requests
from agent.utils.lmm.lmm_utils import encode_image
from agent.planner_critic.task_manager import encode_task

def send_actor_critic_request(url, 
                       current_task,
                       current_action,
                       parsed_screenshot,
                       screenshot_path: str, 
                       software_name: str, 
                       history: list=[], 
                       task_id: str=None, 
                       step_id: str=None,
                       if_screenshot=False):
    """Send a POST request to the server with the query and the image."""
    # Encode the image
    screenshot_data = [encode_image(spath) for spath in screenshot_path]
    
    # Construct the request data
    data = {
        "current_task": encode_task(current_task),
        "current_action": current_action,
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

    return response