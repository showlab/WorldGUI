import os
import json
import logging
import base64
import datetime
import random
import numpy as np

def setup_directories(CACHE_DIR, task_id):
    request_dir = os.path.join(CACHE_DIR, str(task_id), "request")
    response_dir = os.path.join(CACHE_DIR, str(task_id), "response")
    os.makedirs(request_dir, exist_ok=True)
    os.makedirs(response_dir, exist_ok=True)
    return request_dir, response_dir


def save_request_data(data, request_dir, step_id):
    file_path = os.path.join(request_dir, f"data-{step_id}.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    logging.info(f"Saved data to {file_path}")

def save_screenshot_multiple(data, request_dir, step_id):

    screenshot_paths = []
    screen_index = 0
    for data in data['screenshot']:
        screenshot_path = os.path.join(request_dir, f"screenshot-{step_id}-{screen_index}.png")
        with open(screenshot_path, "wb") as fh:
            fh.write(base64.b64decode(data))
        
        screenshot_paths.append(screenshot_path)
        logging.info(f"Saved image to {screenshot_path}")

        screen_index += 1
    return screenshot_paths

def save_screenshot(data, request_dir, step_id):
    screenshot_path = os.path.join(request_dir, f"screenshot-{step_id}.png")
    with open(screenshot_path, "wb") as fh:
        fh.write(base64.b64decode(data["screenshot"]))
    logging.info(f"Saved image to {screenshot_path}")
    return screenshot_path


def generate_task_id():
    # Time-based UUID
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    rand_str = "".join(random.choices(
        "abcdefghijklmnopqrstuvwxyz0123456789", k=5))
    return f"{timestamp}_{rand_str}"


def custom_serializer(value):
    if isinstance(value, (np.integer, np.int64, np.int32)):
        return int(value)
    elif isinstance(value, (np.floating, np.float64, np.float32)):
        return float(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(value, list):
        return [custom_serializer(item) for item in value]
    elif isinstance(value, dict):
        return {key: custom_serializer(val) for key, val in value.items()}
    else:
        return value


def is_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False


def find_non_serializable(data, path=""):
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            if not is_serializable(value):
                print(f"Non-serializable value at {path}: {value}")
                data[key] = custom_serializer(value)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_path = f"{path}[{index}]" if path else f"[{index}]"
            if not is_serializable(item):
                print(f"Non-serializable value at {path}: {item}")
                data[index] = custom_serializer(item)
    else:
        if not is_serializable(data):
            print(f"Non-serializable value at {path}: {data}")