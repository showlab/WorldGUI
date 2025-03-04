import json
import uiautomation as auto
import time
import subprocess
import pygetwindow as gw
from pywinauto import Application, Desktop
import os
import re
import datetime
import requests
import time
from termcolor import colored
import subprocess
import win32gui
import win32process
import psutil
from PIL import Image, ImageDraw
import base64
import pickle
import requests
# from pywinauto.application import Application
from pywinauto.findwindows import find_windows


software_name_map = {"adobe_acrobat": "Adobe Acrobat", "premiere_pro": "Adobe Premiere Pro", "VSCode": "Visual Studio Code", "Youtube": "Google Chrome"}
    
def get_screenshot(software_name):
    software_name = software_name_map.get(software_name, software_name)
    gui = GUICapture()
    meta_data, screenshot_path = gui.capture(software=software_name)
    return meta_data, screenshot_path

# def focus_software(software_name):
#     software_name = software_name_map.get(software_name, software_name)
#     gui = GUICapture()
#     _ = gui.connect_to_application(software_name)
#     print('hehrnyrt', _)
#     all_windows = gui.app.windows()
#     window_names = [window.window_text() for window in all_windows]
#     meta_data = {}
#     for window_name in window_names:
#         if window_name:
#             print(window_name)
#             target_window = gui.app.window(title=window_name)
#             print(target_window)
#             target_window.set_focus()  # ERROR: This line will turn off the right-click menu
#             time.sleep(0.5)
#         # break # only first window

def focus_software(software_name):
    software_name = software_name_map.get(software_name, software_name)
    gui = GUICapture()

    if software_name in ['File Explorer']:
        window_name = gui.connect_to_application(software_name)
        target_window = gui.app.window(title=window_name)
        target_window.set_focus()
    else:
        try:
            _ = gui.connect_to_application(software_name)
            all_windows = gui.app.windows()
            window_names = [window.window_text() for window in all_windows]
            for window_name in window_names:
                if window_name:
                    target_window = gui.app.window(title=window_name)
                    target_window.set_focus()  # ERROR: This line will turn off the right-click menu
                    time.sleep(0.5)
                break ## for chrome tasks
        except Exception:
            # If there's an exception, such as a method failing, we skip it
            pass


def get_control_properties(control, properties_list, no_texts=False):
    prop_dict = {}
    for prop in properties_list:
        # Skip 'texts' property if no_texts flag is set
        if no_texts and prop == 'texts':
            prop_dict[prop] = ['']  # Use an empty list as a placeholder
            continue

        # Check if the control has the property as an attribute
        if hasattr(control, prop):
            attr = getattr(control, prop)
            # Ensure the attribute is callable before attempting to call it
            if callable(attr):
                try:
                    value = attr()
                    # Special handling for 'rectangle' property
                    if prop == 'rectangle':
                        value = [value.left, value.top, value.right, value.bottom]
                    prop_dict[prop] = value
                except Exception:
                    # If there's an exception, such as a method failing, we skip it
                    continue
            else:
                # If the attribute is not callable, directly assign it
                prop_dict[prop] = attr
    return prop_dict


class GUICapture:
    """
    A class to capture and interact with a GUI of a specified application.
    """
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    RED = '\033[91m'
    END = '\033[0m'

    def __init__(self, cache_folder='.cache/'):
        """
        Initialize the GUICapture instance.
        """
        self.task_id = self.get_current_time()
        self.cache_folder = os.path.join(cache_folder, self.task_id)
        os.makedirs(self.cache_folder, exist_ok=True)
        self.current_step = 0
        self.history = []
        self.port = 6007      

    def capture(self, software=None):
        """
        Execute the capture process.
        """
        start = time.time()
        # time.sleep(2)  # Consider explaining why this delay is necessary
        self.connect_to_application(software)
        meta_data = self.get_gui_meta_data(software)
        screenshot_path = self.capture_screenshot()
        print(f"Time used: {time.time() - start}")
        start = time.time()
        return meta_data, screenshot_path
    
    def connect_to_application(self, software_name):
        """
        Connect to the target application.
        """
        if software_name == "File Explorer":
            window_name_list = get_explorer_windows()
            window_name = software_name
            for winname in window_name_list:
                if 'File Explorer' in winname:
                    window_name = winname
            print(f"Connect to the application: {window_name}")
        else:
            window_name = software_name

        try:
            window_handles = find_windows(title_re=f".*{window_name}*", visible_only=False)
            # print(window_handles)
            self.app = Application(backend="uia").connect(handle=window_handles[0])
            # self.app = Application(backend="uia").connect(title_re=f".*{software_name}*")
        except Exception as e:
            print(f"Error connecting to application: {e}")
            try:
                print("Try to connect to the application by using the window name.")
                self.app = self.detect_duplicate_name_windows(window_name)
            except Exception as e:
                print(f"Error connecting to application: {e}")

        return window_name

    def detect_duplicate_name_windows(self, software_name):
        # 使用find_windows函数查找所有匹配的窗口句柄
        window_handles = find_windows(title_re=f".*{software_name}*", visible_only=False)

        # 检查找到的窗口句柄数量
        if window_handles:
            # 假设我们想要连接到找到的第一个窗口
            first_window_handle = window_handles[0]

            # 使用窗口句柄连接到应用程序
            app = Application(backend="uia").connect(handle=first_window_handle)

            return app
            # # 通过app对象操作窗口
            # # 例如，获取窗口的主窗口对象并进行操作
            # main_window = app.window(handle=first_window_handle)
            # # 现在可以对main_window进行操作，例如点击按钮、输入文本等

        else:
            print("没有找到匹配的窗口")
            return None

    def get_gui_meta_data(self, software):
        # Connect to the application
        # Initialize data storage
        control_properties_list = ['friendly_class_name', 'texts', 'rectangle', 'automation_id']
        th = 100 # software_th.get(software, 100)

        def recurse_controls(control, current_depth=0):
            children = control.children()

            child_data = []
            if current_depth > th:
                return []
        
            for child in children:
                # check if the control is visible
                # if not child.is_visible():
                #     continue  

                properties = get_control_properties(child, ['friendly_class_name'])

                # Check if the control is a ComboBox, which may encounter bug while acquire text
                no_texts = True if properties.get('friendly_class_name') == 'ComboBox' else False
                    
                child_data.append({
                    'properties': get_control_properties(child, control_properties_list, no_texts=no_texts),
                    'children': recurse_controls(child, current_depth + 1)
                })

            return child_data

        all_windows = self.app.windows()

        window_names = [window.window_text() for window in all_windows]

        window_names = [item for item in window_names if item]

        meta_data = {}
        for window_name in window_names:
            if window_name:
                print(window_name)
                target_window = self.app.window(title=window_name)
                print(target_window)
                # target_window.set_focus()

                # Traverse the control tree
                meta_data[window_name] = recurse_controls(target_window)
            break # only first window
        return meta_data

    def capture_screenshot(self, save_path=None):
        # save screenshot and return path
        if save_path:
            screenshot_path = save_path
        else:
            screenshot_path = os.path.join(self.cache_folder, f'screenshot-{self.current_step}.png')

        screenshot = auto.GetRootControl().ToBitmap()
        screenshot.ToFile(screenshot_path)
        return screenshot_path

    @staticmethod
    def get_current_time():
        return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


def get_all_windows():
    all_windows = gw.getAllWindows()
    all_windows_name = [win.title for win in all_windows if win.title]
    all_windows_name = simplify_window_names(all_windows_name)
    return all_windows_name


def simplify_window_names(names):
    simplified_names = []
    for name in names:
        # Split the name by '-' and strip whitespace
        parts = [part.strip() for part in name.split('-')]
        # Use the part after the last '-' if available, otherwise the original name
        simplified_name = parts[-1] if len(parts) > 1 else name
        simplified_names.append(simplified_name)
    return simplified_names


def open_software(software_name):
    windows = gw.getWindowsWithTitle(software_name)

    name2exe = {"calculator": "calc.exe"}

    if windows:
        print("Calculator is already open.")
        for window in windows:
            window.close()  # Close each window that matches
        time.sleep(2)  # Wait for the software to close completely
    else:
        print("Calculator is not open, opening now.")

    subprocess.Popen(name2exe[software_name.lower()])
    time.sleep(2)

    maximize_window(software_name)


def maximize_window(title):
    """Maximize the window"""
    windows = gw.getWindowsWithTitle(title)
    if windows:
        window = windows[0]  # Assume the first window is target window
        if not window.isMaximized:
            window.maximize()
            print(f"Window '{title}' has been maximized.")
        else:
            print(f"Window '{title}' is already maximized.")
    else:
        print(f"No window with the title '{title}' found.")


def web_collector(capture, url, save_folder="website"):
    save_path = os.path.join(save_folder, url_to_filename(url))
    response = capture.run("None", software='Chrome', send_data=True, run_code=False, reset=True,
                           port=6007, save_path=f"{save_path}.png")
    json.dump(response.json()['gui'], open(f"{save_path}.json", "w"))

    print(f"The meta data is saved in {save_path}.json & {save_path}.png")


def url_to_filename(url):
    # Remove illegal characters for filenames
    # You might also want to remove or replace HTTP protocols and such to make it more readable
    filename = url.replace('http://', '').replace('https://', '').replace('www.', '')
    # These include: \ / : * ? " < > |
    # Replace illegal characters with underscores or another preferred character
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    # Shorten the filename or split if necessary to avoid overly long filenames
    if len(filename) > 255:  # Typical max length for file systems
        filename = filename[:255]
    return filename


def get_explorer_windows():
    explorer_windows = []

    def enum_window_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and len(win32gui.GetWindowText(hwnd)) > 0:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                if process.name() == "explorer.exe":
                    explorer_windows.append(win32gui.GetWindowText(hwnd))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    win32gui.EnumWindows(enum_window_callback, None)
    return explorer_windows

def visualize(gui, screenshot_path, if_show=True):
    ui_elements = []
    for window_name, panels in gui.items():
        for panel in panels:
            for row in panel['elements']:
                ui_elements.append(row)
                # for element in row:
                #     ui_elements.append(element)
                    
    image = Image.open(screenshot_path)
    draw = ImageDraw.Draw(image)

    # Update elements to draw red rectangles and text in red above the rectangles
    for element in ui_elements:
        name = element['name'].encode('latin-1', 'ignore').decode('latin-1')
        rectangle = element['rectangle']
        # Draw rectangle in red
        draw.rectangle(rectangle, outline="red")
        # Calculate text position above the rectangle
        text_position = (rectangle[0], rectangle[1] - 15)  # Positioned above the rectangle
        draw.text(text_position, name, fill="red")  # Default font

    # Display the image in Jupyter
    image.show()
    return image


def encode_image(image_path):
    """Encode image file to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
def encode_task(task):
    if isinstance(task, str):
        return task
    else:
        return base64.b64encode(pickle.dumps(task)).decode('utf-8')
    
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


def send_actor_request(url, 
                       current_task, 
                       parsed_screenshot,
                       screenshot_path: str, 
                       software_name: str, 
                       history: list=[], 
                       error_message: str="", 
                       next_step_tip: str="", 
                       pre_act_success_flag: bool=False, 
                       pre_act_resume_flag: bool=False, 
                       task_id: str=None, 
                       step_id: str=None):
    """Send a POST request to the server with the query and the image."""
    # Encode the image
    screenshot_data = encode_image(screenshot_path)
        
    # Construct the request data
    data = {
        "current_task": encode_task(current_task),
        "parsed_screenshot": parsed_screenshot,
        "screenshot": screenshot_data,
        "history": history,
        "error_message": error_message,
        "next_step": next_step_tip,
        "pre_act_success_flag": pre_act_success_flag,
        "pre_act_resume_flag": pre_act_resume_flag,
        "software_name": software_name,
        "task_id": task_id,
        "step_id": step_id, 
    }
    
    # Send POST request
    response = requests.post(url, json=data)
    return response.json()

if __name__ == '__main__':
    capture = GUICapture()
    meta_data, screenshot_path = capture.capture(software="Word")

    print('sdsdsdsdd', meta_data)