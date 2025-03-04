import requests
from agent.utils.lmm.lmm_utils import encode_image

def send_planner_request(url, screenshot_path: str, query: str, software_name: str, task_id: str = None, gui_info: dict = None, video_path: str = None):
    """Send a POST request to the server with the query and the image."""
    # Encode the image
    screenshot_data = encode_image(screenshot_path)
    
    # Construct the request data
    data = {
        "query": query, 
        "software_name": software_name,
        "task_id": task_id, 
        "screenshot": screenshot_data,
        "gui_info": gui_info,
        "video_path": video_path
    }
    
    # Send POST request
    response = requests.post(url, json=data)
    return response.json()