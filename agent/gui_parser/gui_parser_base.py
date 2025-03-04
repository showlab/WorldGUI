import cv2
import numpy as np
# import datetime
# import importlib
import textdistance
from agent.base_module import BaseModule
from agent.gui_parser.ui_text_detection import text_detection
from agent.gui_parser.button_detection import *
from agent.gui_parser.utils import *
# from ultralytics import YOLO


# from ui_text_detection import text_detection
# from button_detection import detect_button
# from utils import crop_panel, restore_coordinate, get_current_time, is_in_bbox


class GUIParserBase(BaseModule):
    name = "gui_parser"
    description = (
        '''
This tool can extract the information of screenshot.
Invoke command: gui_parser(query, visual[i])
:param query -> str, specific command. visual[i] -> image, the latest screenshot.
''')

    def __init__(self):
        # judge if the cache folder exists
        super(GUIParserBase, self).__init__()
        # self.cache_folder = cache_folder
        # self.task_id = get_current_time()
        # YOLOv8 model that can detect 600 classes
        # self.yolo_model = self.build_model("yolov8")
        # self.parsers = []

    def _run(self, meta_data, screenshot_path, software_name=None):
        # get main panel
        self.software_name = software_name
        self.screenshot_paths.append(screenshot_path)
        self.parsed_gui = {'panel': []}

        if self.software_name in ['Calculator', '计算器', '任务栏', 'Taskbar', 'Xshell', 'RStudio', 'Zoom', 'Tecent meeting', 'Power BI', 'web']:
            self.parsed_gui = self.get_panel_uia(meta_data)
            # Template matching for these apllications
            for panel_item in self.parsed_gui['panel']:
                if panel_item['name'] not in ['Title Bar','Navigation Bar']:
                    button_box = self.get_button(panel_item, self.screenshot_paths[-1])
                    panel_item['elements'] += button_box
            return self.parsed_gui
        
        highlight_ocr = self.detect_highlight_with_ocr(screenshot_path)
        _, ocr = text_detection(screenshot_path, save_png=False)

        for window_name, window_meta_data in meta_data.items():
            if not window_meta_data:
                continue
            if window_meta_data[0]['properties']['friendly_class_name'] in ['MenuItem', 'Edit', 'Button']:
                self.parsed_gui['panel'] += self.get_popup_window(window_meta_data, window_name)
            else:
                self.parsed_gui['panel'] += self.get_panel(window_meta_data, ocr, highlight_ocr)
                self.parsed_gui['panel'] += self.get_menu(window_meta_data)
                # TODO: get the title bar

        return self.parsed_gui

    def reset(self):
        self.screenshot_paths = []
        self.task_id = get_current_time()

    
    def postprocess_uia(self, metadata):
        # iterate each window
        for window_data in metadata.values():
            
            for element_data in window_data:
                # get all elements of current level
                elements = element_data.get('elements', [])
                
                # if the class name is TitleBar, regain the rectangle of the whole panel
                if element_data['class_name'] == 'TitleBar' and len(elements) > 0:
                    left = min(e.get('rectangle', [0, 0, 0, 0])[0] for e in elements)
                    top = min(e.get('rectangle', [0, 0, 0, 0])[1] for e in elements)
                    right = max(e.get('rectangle', [0, 0, 0, 0])[2] for e in elements)
                    bottom = max(e.get('rectangle', [0, 0, 0, 0])[3] for e in elements)
                    element_data['rectangle'] = [left, top, right, bottom]

                # sort elements by x and y
                element_data['elements'] = sort_elements_by_xy(elements)
                

        return metadata

    # retreieve the panel meta data directively from UIA (pywinauto)
    def get_panel_uia(self, control_info_list, screenshot_path):

        text2panel_name = {'新建会话属性': 'New session properties',
                           '会话管理器': 'Session manager'
                           }

        def recurse_controls(control_info, dialog_components, depth):

            children = control_info['children']
            if len(children) == 0:
                return

            for child_control in children:
                child_properties = child_control['properties']
                child_friendly_class_name = child_properties['friendly_class_name']
                child_properties_name = ''

                # Get the feasible name of the child control
                if len(child_properties['texts']) == 0:
                    child_properties_name = ''  
                elif isinstance(child_properties['texts'][0],list) and len(child_properties['texts']) != 0:
                    result = []
                    for item in child_properties['texts']:
                        if isinstance(item[0], str):
                            result.append(''.join(item))
                    child_properties_name = ''.join(result)
                else:
                    child_properties_name = child_properties['texts'][0]

                # Get the search bar
                if child_friendly_class_name in ['Edit', 'ComboBox'] and (child_properties_name == ''):  # or 'search' not in child_properties_name.lower()
                    child_properties_name = 'Search Bar'

                # Rules to exclude some class name 
                # if self.software_name == 'Xshell':
                #     exclude_class_name_list = ['GroupBox', 'ListBox', 'Custom', 'Menu', 'Pane', 'Toolbar', 'TabControl', 'DataItem']
                # elif self.software_name == 'RStudio':
                #     exclude_class_name_list = ['GroupBox', 'ListBox', 'Custom', 'Menu', 'Pane', 'Toolbar', 'TabControl', 'DataItem', 'TabItem', 'MenuItem', 'Button', 'Document']
                # elif self.software_name == 'web video':
                #     exclude_class_name_list = ['GroupBox', 'ListBox', 'ListItem', 'Custom', 'Menu', 'Pane', 'Toolbar', 'TabControl', 'TreeItem', 'DataItem']
                # else:
                #     exclude_class_name_list = ['GroupBox', 'ListBox', 'ListItem', 'Custom', 'Menu', 'Pane', 'Toolbar', 'TabControl', 'TreeItem', 'DataItem', 'Hyperlink']


                if  ('search' in child_properties_name.lower() and child_friendly_class_name == 'GroupBox') or (child_friendly_class_name not in self.exclude_class_name_list
                                or len(child_control['children']) == 0) and (child_properties_name not in ['', '"']) and (not all(element == 0 for element in child_properties['rectangle'])):
                                
                    left, top, right, bottom = child_properties['rectangle']
                    left_bound, top_bound, right_bound, bottom_bound = dialog_components['rectangle']
                    
                    if self.software_name not in ['word', 'excel', 'powerpoint']:
                        if left < left_bound:
                            child_properties['rectangle'][0] = left_bound
                        if top < top_bound:
                            child_properties['rectangle'][1] = top_bound
                        if right > right_bound:
                            child_properties['rectangle'][2] = right_bound
                        if bottom > bottom_bound:
                            child_properties['rectangle'][3] = bottom_bound

                    if not (child_properties['rectangle'][0] >= child_properties['rectangle'][2] or child_properties['rectangle'][1] >= child_properties['rectangle'][3]):
                        panel_img = crop_panel(child_properties['rectangle'], screenshot_path)
                        if child_friendly_class_name in ['CheckBox'] or not np.all(panel_img == panel_img[0, 0]):
                            # remove unseen characters
                            child_properties_name = child_properties_name.replace('\u200b', '')

                            dialog_components['elements'].append({
                                'name': child_properties_name,
                                'rectangle': child_properties['rectangle'],
                                'class_name': child_friendly_class_name,
                                'type': ['Click', 'rightClick'],
                                'depth': depth + '-' + str(self.count)
                            })

                            self.count += 1

                # Post-processing for Outlook
                if child_friendly_class_name in ['Button', 'MenuItem', 'TabItem'] and self.software_name == 'outlook':
                    continue
                
                recurse_controls(child_control, dialog_components, depth)
    
        
        main_name = list(control_info_list.keys())[0]
        dialog_components = {self.software_name: []}
        excel_iter = iter(['Navigation Bar', 'Tools Bar', 'Function Bar', 'Main Content'])
        # if any(keyword in main_name for keyword in ['哔哩哔哩', 'bilibili', '腾讯视频']):
        #     self.software_name = 'web video'


        # Check if the friendly_class_name
        for control_info in control_info_list[main_name]:

            if control_info['properties']['friendly_class_name'] in ['Dialog', 'Pane', 'GroupBox', 'TitleBar', 'Menu', 'Document', 'ListBox'] and len(control_info['children']) != 0:
                # Append texts and rectangle to the Dialog components
                # if all(element <= 0 for element in control_info['properties']['rectangle']) and \
                #             control_info['properties']['friendly_class_name'] not in ['TitleBar']:
                #     continue

                # Main panel name rules
                control_name = control_info['properties']['texts'][0]
                if control_info['properties']['texts'][0] == '':
                    if control_info['properties']['friendly_class_name'] == 'TitleBar':
                        control_name = 'Title Bar'

                    if control_info['properties']['friendly_class_name'] == 'Document':
                        control_name = 'Main Content'
                        
                    if control_info['properties']['friendly_class_name'] == 'Pane':
                        if self.software_name in ['web', 'web video']:
                            control_name = 'Navigation Bar'
                        else:
                            if self.software_name == 'excel': 
                                control_name = next(excel_iter, 'Main Content')
                            else:
                                control_name = 'Main Content'
                else:
                    if control_info['properties']['friendly_class_name'] == 'Document' and self.software_name in ['web', 'web video']:
                        control_name = 'Main Content'
                        # if 'Outlook' in main_name and 'Mail' in main_name:
                        #     original_value = dialog_components.pop(self.software_name)
                        #     self.software_name = 'Outlook'
                        #     dialog_components['Outlook'] = original_value
                    else:
                        control_name = control_info['properties']['texts'][0]

                if control_name in text2panel_name.keys():
                    control_name = text2panel_name[control_name]

                self.count = 1
                dialog_components[self.software_name].append({
                    'name': control_name,
                    'rectangle': control_info['properties']['rectangle'],
                    'class_name': control_info['properties']['friendly_class_name'],
                    'depth': '1',
                    'elements': []
                })

                # Process children of the Dialog
                recurse_controls(control_info, dialog_components[self.software_name][-1], '1')

        return dialog_components
    
    
    def get_panel_uia_ocr(self, control_info_list, screenshot_path):

        def recurse_controls(control_info, dialog_components, type='normal', depth = 1):

            children = control_info['children']
            if len(children) == 0:
                return

            for child_control in children:
                child_properties = child_control['properties']
                child_friendly_class_name = child_properties['friendly_class_name']
                child_properties_name = ''

                # Get the feasible name of the child control
                if len(child_properties['texts']) == 0:
                    child_properties_name = ''  
                elif isinstance(child_properties['texts'][0],list) and len(child_properties['texts']) != 0:
                    result = []
                    for item in child_properties['texts']:
                        if isinstance(item[0], str):
                            result.append(''.join(item))
                    child_properties_name = ''.join(result)
                else:
                    child_properties_name = child_properties['texts'][0]

                # Get the search bar
                if child_friendly_class_name in ['Edit', 'ComboBox'] and (child_properties_name == '' or 'search' not in child_properties_name.lower()):
                        child_properties_name = 'Search Bar'

                conditions = {
                    'static': (
                        child_friendly_class_name == 'CheckBox' and
                        child_properties_name not in ['', '"'] and
                        not all(element == 0 for element in child_properties['rectangle']),
                        dialog_components['rectangle']
                    ),
                    'normal': (
                        'search' in child_properties_name.lower() and
                        child_friendly_class_name == 'GroupBox' or
                        (child_friendly_class_name not in self.exclude_class_name_list or
                        len(child_control['children']) == 0) and
                        child_properties_name not in ['', '"'] and
                        not all(element == 0 for element in child_properties['rectangle']),
                        dialog_components['rectangle']
                    )
                }

                if conditions.get(type, (False, None))[0]:
                    left, top, right, bottom = child_properties['rectangle']
                    left_bound, top_bound, right_bound, bottom_bound = dialog_components['rectangle']
                    
                    if self.software_name not in ['word', 'excel', 'powerpoint']:
                        if left < left_bound:
                            child_properties['rectangle'][0] = left_bound
                        if top < top_bound:
                            child_properties['rectangle'][1] = top_bound
                        if right > right_bound:
                            child_properties['rectangle'][2] = right_bound
                        if bottom > bottom_bound:
                            child_properties['rectangle'][3] = bottom_bound

                    if not (child_properties['rectangle'][0] >= child_properties['rectangle'][2] or child_properties['rectangle'][1] >= child_properties['rectangle'][3]):
                        # remove unseen characters
                        child_properties_name = child_properties_name.replace('\u200b', '')

                        dialog_components['elements'].append({
                            'name': child_properties_name,
                            'rectangle': child_properties['rectangle'],
                            'class_name': child_friendly_class_name,
                            'type': ['Click', 'rightClick'],
                            'depth': depth + '-' + str(self.count)
                        })

                        self.count += 1

                recurse_controls(child_control, dialog_components, type, depth)

        
        main_name = list(control_info_list.keys())[0]
        dialog_components = {self.software_name: []}

        # Check if the friendly_class_name
        for control_info in control_info_list[main_name]:

            if control_info['properties']['friendly_class_name'] in ['Dialog', 'Pane', 'GroupBox', 'TitleBar', 'Menu', 'Document', 'ListBox'] and len(control_info['children']) != 0:
                # Append texts and rectangle to the Dialog components
                # if all(element == 0 for element in control_info['properties']['rectangle']):
                #     continue

                # Main panel name rules
                control_name = control_info['properties']['texts'][0]
                if control_info['properties']['texts'][0] == '':
                    if control_info['properties']['friendly_class_name'] == 'TitleBar':
                        control_name = 'Title Bar'

                    if control_info['properties']['friendly_class_name'] == 'Document':
                        control_name = 'Main Content'
                        
                    if control_info['properties']['friendly_class_name'] == 'Pane':
                        if self.software_name in ['web', 'web video', 'web ocr', 'powerpoint']:
                            control_name = 'Navigation Bar'
                        else:
                            control_name = 'Main Content'
                else:
                    if control_info['properties']['friendly_class_name'] == 'Document' and self.software_name in ['web', 'web video', 'web ocr', 'powerpoint']:
                        control_name = 'Main Content'
                        # if 'Outlook' in main_name and 'Mail' in main_name:
                        #     original_value = dialog_components.pop(self.software_name)
                        #     self.software_name = 'Outlook'
                        #     dialog_components['Outlook'] = original_value
                    else:
                        control_name = control_info['properties']['texts'][0]


                self.count = 1
                dialog_components[self.software_name].append({
                    'name': control_name,
                    'rectangle': control_info['properties']['rectangle'],
                    'class_name': control_info['properties']['friendly_class_name'],
                    'depth': '1',
                    'elements': []
                })

                # Process children of the Dialog
                if control_name == 'Main Content':
                    recurse_controls(control_info, dialog_components[self.software_name][-1], type='static', depth = '1')
                else:
                    recurse_controls(control_info, dialog_components[self.software_name][-1], depth = '1')

        return dialog_components



    @staticmethod
    def merge_elements(panel_item):
        # print(panel_item)
        empty = True
        for k, v in panel_item.items():
            if v:
                empty = False
                break

        if empty:
            return []

        merged_control, elements_to_be_merged = [], []
        for key, value in panel_item.items():
            if not merged_control:
                # if key == 'button':
                #     merged_control = [row for row in panel_item[key]]
                # else:
                #     merged_control = [list(row) for row in panel_item[key]]
                if key == 'editing_control':
                    merged_control = [list(row) for row in panel_item[key]]
                else:
                    elements_to_be_merged += panel_item.get(key, [])
            else:
                elements_to_be_merged += panel_item.get(key, [])
        
        for button in elements_to_be_merged:
            y_center = (button['rectangle'][1] + button['rectangle'][3]) / 2
            row_index = find_appropriate_row(merged_control, y_center)
            if row_index is not None:
                insert_into_row(merged_control[row_index], button)
            else:
                # If button doesn't fit into any row, append it as a new row.
                merged_control.append([button])

        # Sort rows from top to bottom based on the center y-coordinate of the first element
        try:
            merged_control.sort(key=lambda row: ((row[0]['rectangle'][1] + row[0]['rectangle'][3]) / 2, (row[0]['rectangle'][0] + row[0]['rectangle'][2]) / 2))
        except:
            print(merged_control)
        return merged_control

    @staticmethod
    def get_menu(meta_data):
        # get menu item
        menu_item = []
        for item in meta_data:
            if item['properties']['friendly_class_name'] == 'Menu':
                # only keep one level children
                new_item = {'name': item['properties']['texts'][0],
                            'rectangle': item['properties']['rectangle'],
                            'elements': [[{'name': child['properties']['texts'][0],
                                           'rectangle': child['properties']['rectangle'],
                                           } for child in item['children'] if child['properties']['texts']]]
                            }
                menu_item.append(new_item)
        return menu_item

    @staticmethod
    def get_title_bar(meta_data):
        pass

    def get_button(self, panel_item, screenshot_path):
        # crop the panel based on the rectangle
        print("processing button")
        print(panel_item['name'], panel_item['rectangle'])
        panel_img = crop_panel(panel_item['rectangle'], screenshot_path)
        # get the button
        # th = 0.90 if self.software_name == 'after effect' else 0.78
        th = 0.90 if self.software_name == 'after effect' else 0.78
        if self.software_name in ['premiere', 'after effect']:
            button_box =  detect_button_pr_ae(panel_img, software_name=self.software_name, panel_name=panel_item['name'],
                                   threshold=th)
        else:
            button_box = detect_button(panel_img, software_name=self.software_name, panel_name=panel_item['name'],
                                   threshold=th)

        if self.software_name == 'after effect' and panel_item['name'] == 'Timeline':
            hsv = cv2.cvtColor(panel_img, cv2.COLOR_BGR2HSV)

            # 定义灰色的 HSV 范围
            lower_gray = np.array([0, 0, 46])
            upper_gray = np.array([180, 40, 220])

            # 创建掩膜，将在指定颜色范围内的部分设置为白色，其他部分设置为黑色
            mask = cv2.inRange(hsv, lower_gray, upper_gray)

            # 将原始图像与掩膜进行按位与操作，提取对应部分
            result = cv2.bitwise_and(panel_img, panel_img, mask=mask)

            result = process_image_highlight_gray(result)
            result = np.repeat(result[..., np.newaxis], 3, 2)

            save_path = self.cache_folder + "gray.png"
            cv2.imwrite(save_path, result)

            check_box = detect_button(result, software_name=self.software_name, panel_name=panel_item['name'],
                                      threshold=0.9)
            button_box += check_box
            print(check_box, panel_item['name'])

        # restore the button coordinate to the whole screenshot
        button_box = restore_coordinate(button_box, panel_item['rectangle'])
        return button_box

    @staticmethod
    def get_text(panel_item, ocr, screenshot_path, type=None):
        # Step1: Find all the texts in the panel
        panel_texts = [item for item in ocr['texts'] if is_in_bbox(item['bbox'], panel_item['rectangle'])]

        if not panel_texts:
            return []

        # obtain information about panel texts
        sorted_panel_texts = sorted(panel_texts, key=lambda x: (x['bbox'][1], x['bbox'][0]))

        # Step 2: Identify rows by grouping elements that are in approximately the same vertical position.
        editing_controls = []
        current_row = []
        previous_y = sorted_panel_texts[0]['bbox'][1]
        action_dict = {
            'Effect Controls': ['click', 'rightClick'],
            'Project': ['click', 'rightClick', 'doubleClick', 'dragTo_timeline'],
            'Effects': ['click', 'rightClick', 'dragTo_block'],
            'Effects & Presets': ['click', 'rightClick', 'dragTo_timeline']
        }
        
        count = 1
        for item in sorted_panel_texts:
            y1 = item['bbox'][1]

            # If the vertical position of the current item is significantly different from the previous one, start a new row.
            if abs(y1 - previous_y) > 15:  # You might need to adjust this threshold based on your panel_texts.
                editing_controls.append(current_row)
                current_row = []

            if type == 'web':
                current_row.append({"name": item['content'], "rectangle": item['bbox'], 'depth': '1-' + str(count), "type": action_dict.get(panel_item['name'], ['click', 'rightClick', 'doubleClick'])})
                count += 1
            else:
                current_row.append({"name": item['content'], "rectangle": item['bbox'], "type": action_dict.get(panel_item['name'], ['click', 'rightClick', 'doubleClick'])})
            previous_y = y1

        # Add the last row if not empty.
        if current_row:
            editing_controls.append(current_row)

        # Step 3: Sort elements within each row based on their horizontal position.
        for i, row in enumerate(editing_controls):
            editing_controls[i] = sorted(row, key=lambda x: x['rectangle'][0])
        return editing_controls

    @staticmethod
    def get_text_4explorer(panel_item, ocr, screenshot_path, type=None):
        # Step1: Find all the texts in the panel
        panel_texts = [item for item in ocr['texts']]

        if not panel_texts:
            return []

        # obtain information about panel texts
        sorted_panel_texts = sorted(panel_texts, key=lambda x: (x['bbox'][1], x['bbox'][0]))

        # Step 2: Identify rows by grouping elements that are in approximately the same vertical position.
        editing_controls = []
        current_row = []
        previous_y = sorted_panel_texts[0]['bbox'][1]
        action_dict = {
            'Effect Controls': ['click', 'rightClick'],
            'Project': ['click', 'rightClick', 'doubleClick', 'dragTo_timeline'],
            'Effects': ['click', 'rightClick', 'dragTo_block'],
            'Effects & Presets': ['click', 'rightClick', 'dragTo_timeline']
        }
        
        count = 1
        for item in sorted_panel_texts:
            y1 = item['bbox'][1]

            # If the vertical position of the current item is significantly different from the previous one, start a new row.
            if abs(y1 - previous_y) > 15:  # You might need to adjust this threshold based on your panel_texts.
                editing_controls.append(current_row)
                current_row = []

            if type == 'web':
                current_row.append({"name": item['content'], "rectangle": item['bbox'], 'depth': '1-' + str(count), "type": action_dict.get(panel_item['name'], ['click', 'rightClick', 'doubleClick'])})
                count += 1
            else:
                current_row.append({"name": item['content'], "rectangle": item['bbox'], "type": action_dict.get(panel_item['name'], ['click', 'rightClick', 'doubleClick'])})
            previous_y = y1

        # Add the last row if not empty.
        if current_row:
            editing_controls.append(current_row)

        # Step 3: Sort elements within each row based on their horizontal position.
        for i, row in enumerate(editing_controls):
            editing_controls[i] = sorted(row, key=lambda x: x['rectangle'][0])
        return editing_controls

    def get_editing_control_icons(self, panel_item, screenshot_path):
        # crop the panel based on the rectangle
        panel_img = crop_panel(panel_item['rectangle'], screenshot_path)
        # get the button
        button_box = detect_button(panel_img, software_name=self.software_name, panel_name=panel_item['name'],
                                   icon_type='editing_control')
        # restore the button coordinate to the whole screenshot
        button_box = restore_coordinate(button_box, panel_item['rectangle'])
        return button_box

    @staticmethod
    def get_scroll(panel_item, button_list, ocr, screenshot_path):
        if panel_item['name'] not in ['Lumetri Color']:
            return []

        # TODO: first detect the circle, then use 霍夫变化 to detect the line?
        scroll_button = [b for b in button_list if 'scroll bar' in b['name']]
        scroll_text = [t for t in ocr['texts'] if is_in_bbox(t['bbox'], panel_item['rectangle'])]

        scroll_bar_items = []
        for button in scroll_button:
            l, t, r, b = button['rectangle']
            cur_bar = {"Button center": ((l + r) // 2, (t + b) // 2)}
            rectangle = [None, None, None, None]

            for text in scroll_text:
                # Find scroll bar name
                if 0 < abs(text['bbox'][1] - button['rectangle'][1]) < 10 and 0 < button['rectangle'][0] - text['bbox'][
                    0] < 500:
                    cur_bar['name'] = text['content']
                    rectangle[0] = text['bbox'][0]
                    rectangle[1] = text['bbox'][1]
                    rectangle[3] = text['bbox'][3]
                # Find current value of the scroll bar
                elif 0 < abs(text['bbox'][1] - button['rectangle'][1]) < 10 and 0 < text['bbox'][0] - \
                        button['rectangle'][0] < 500:
                    cur_bar['cur_value'] = text['content']
                    rectangle[2] = text['bbox'][2]

            # Detect lines use houghLinesP
            scroll_image = crop_panel(rectangle, screenshot_path)
            gray = cv2.cvtColor(scroll_image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

            if lines is not None and len(lines) > 0:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    scroll_bar = [x1, y1, x2, y2]
                    if None in rectangle:
                        break
                    else:
                        cur_bar['rectangle'] = scroll_bar
                        cur_bar['type'] = ['click']
                        cur_bar = restore_coordinate([cur_bar], rectangle)[0]
                        scroll_bar_items.append(cur_bar)

                    # cv2.line(scroll_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    # cv2.imwrite("/home/aiassist/difei/assistgui/.cache/scroll.png", scroll_image)
                    break

            # scroll_bar_items.append(cur_bar)

        return scroll_bar_items
    

    def get_drag_position_pr(self, panel_img):
        hsv = cv2.cvtColor(panel_img, cv2.COLOR_BGR2HSV)

        # Define the scope of gray
        lower_gray = np.array([0, 0, 40])
        # upper_gray = np.array([0, 0, 50])
        upper_gray = np.array([0, 5, 55])

        mask = cv2.inRange(hsv, lower_gray, upper_gray)
        result = cv2.bitwise_and(panel_img, panel_img, mask=mask)
        non_blue_part = cv2.bitwise_not(mask)
        result[non_blue_part > 0] = 255

        save_path = '.cache/' + "cur_pane_gray.png"
        cv2.imwrite(save_path, result)

        panel_img = cv2.imread('.cache/' + "cur_pane_gray.png")
        gray = cv2.cvtColor(panel_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is not None and len(lines) > 0:
            lines = np.squeeze(lines, axis=1)
            # find the first and last horizontal line
            horizontal_lines = lines[(lines[:, 1] == lines[:, 3]) & (lines[:, 0] < lines[:, 2])]
            if len(horizontal_lines) != 0:
                horizontal_lines = horizontal_lines[np.argsort(horizontal_lines[:, 1])]
                first_horizontal_line = horizontal_lines[0]
                last_horizontal_line = horizontal_lines[-1]

            # find the first and last vertical line
            vertical_lines = lines[(lines[:, 0] == lines[:, 2]) & (lines[:, 3] < lines[:, 1])]
            if len(vertical_lines) != 0:
                vertical_lines = vertical_lines[np.argsort(vertical_lines[:, 0])]
                first_vertical_line = vertical_lines[0]
                last_vertical_line = vertical_lines[-1]

            # return the final bounding box
            bounding_box = None
            if len(horizontal_lines) != 0 and len(vertical_lines) != 0:
                # bounding_box = [first_vertical_line[0] + panel_item['rectangle'][0], first_horizontal_line[1] + panel_item['rectangle'][1], 
                #                 last_vertical_line[2] + panel_item['rectangle'][2], last_horizontal_line[3] + panel_item['rectangle'][3]]
                bounding_box = [first_vertical_line[0], first_horizontal_line[1], 
                                last_vertical_line[2], last_horizontal_line[3]]

                cv2.rectangle(panel_img, (first_vertical_line[0], first_horizontal_line[1]), (last_vertical_line[2], last_horizontal_line[3]), (0, 255, 0), 2)
                cv2.imwrite('.cache/' + "cur_pane_gray_line.png", panel_img)
            
            return bounding_box
        
        
    def get_drag_position_ae(self, panel_img):
        hsv = cv2.cvtColor(panel_img, cv2.COLOR_BGR2HSV)

        # Define the scope of gray
        lower_gray = np.array([0, 0, 0])
        upper_gray = np.array([20, 20, 20])

        mask = cv2.inRange(hsv, lower_gray, upper_gray)
        result = cv2.bitwise_and(panel_img, panel_img, mask=mask)
        non_blue_part = cv2.bitwise_not(mask)
        result[non_blue_part > 0] = 255

        save_path = '.cache/' + "cur_pane_gray.png"
        cv2.imwrite(save_path, result)

        panel_img = cv2.imread('.cache/' + "cur_pane_gray.png")
        gray = cv2.cvtColor(panel_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is not None and len(lines) > 0:
            lines = np.squeeze(lines, axis=1)
            # find the first and last horizontal line
            horizontal_lines = lines[(lines[:, 1] == lines[:, 3]) & (lines[:, 0] < lines[:, 2])]
            if len(horizontal_lines) != 0:
                horizontal_lines = horizontal_lines[np.argsort(horizontal_lines[:, 1])]
                first_horizontal_line = horizontal_lines[0]
                last_horizontal_line = horizontal_lines[-1]

            # find the first and last vertical line
            vertical_lines = lines[(lines[:, 0] == lines[:, 2]) & (lines[:, 3] < lines[:, 1])]
            if len(vertical_lines) != 0:
                vertical_lines = vertical_lines[np.argsort(vertical_lines[:, 0])]
                first_vertical_line = vertical_lines[0]
                # last_vertical_line = vertical_lines[-1]

            # return the final bounding box
            bounding_box = None
            if len(horizontal_lines) != 0 and len(vertical_lines) != 0:
                # bounding_box = [first_vertical_line[0] + panel_item['rectangle'][0], first_horizontal_line[1] + panel_item['rectangle'][1], 
                #                 last_vertical_line[2] + panel_item['rectangle'][2], last_horizontal_line[3] + panel_item['rectangle'][3]]
                bounding_box = [first_vertical_line[0], first_horizontal_line[1], 
                                first_horizontal_line[2], last_horizontal_line[3]]

                cv2.rectangle(panel_img, (first_vertical_line[0], first_horizontal_line[1]), (first_horizontal_line[2], last_horizontal_line[3]), (0, 255, 0), 2)
                cv2.imwrite('.cache/' + "cur_pane_gray_line.png", panel_img)
            
            return bounding_box

    def get_timeline(self, panel_item, screenshot_path):
        # TODO: Locate the text display the text
        # if panel_item['name'] not in ['Timeline', 'Program', 'Accessory']:
        #     return [], None, []

        scroll_image = crop_panel(panel_item['rectangle'], screenshot_path)
        # Transform image format from BGR to HSV
        hsv = cv2.cvtColor(scroll_image, cv2.COLOR_BGR2HSV)

        # Define the scope of blue
        lower_blue = np.array([105, 100, 100])
        upper_blue = np.array([130, 255, 255])

        # Creates a mask that sets parts within a specified color range to white and other parts to black
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Perform a bitwise AND operation on the original image and the mask to extract the blue part
        result = cv2.bitwise_and(scroll_image, scroll_image, mask=mask)
        save_path = self.cache_folder + "blue.png"

        cv2.imwrite(save_path, result)
        _, ocr = text_detection(save_path, save_png=False)
        
        cv2.imwrite(self.cache_folder + "cur_pane_timeline.png", scroll_image)
        _, ocr_cur = text_detection(self.cache_folder + "cur_pane_timeline.png", save_png=False)

        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

        timeline = []
        bbox_list = []
        playhead = None
        horizontal_line = None
        drag_position = None
        timeline_flag = False
        if lines is not None and len(lines) >= 2:

            # store the position of action dragTo
            if self.software_name == 'premiere':
                drag_position = self.get_drag_position_pr(scroll_image)
            else:
                drag_position = self.get_drag_position_ae(scroll_image)
                
            if drag_position is not None:
                drag_position = [{'name': 'dragTo_timeline', 'rectangle': drag_position}]
                # drag_position = restore_coordinate(drag_position, panel_item['rectangle'])

            for line in lines:
                x1, y1, x2, y2 = line[0]
                rectangle = [x1, y1, x2, y2]

                # Do not consider boarder lines
                if x1 > 5 and x1 <= x2 < panel_item['rectangle'][2] - panel_item['rectangle'][0] - 5:
                    if playhead is None and x2 - x1 < 3: 
                        timeline.append({'name': 'playhead', 'rectangle': rectangle, 'type': self.action_type + ['dragTo_timeline']})
                    else:
                        bbox_list.append(rectangle)
            
                cv2.line(result, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.imwrite('.cache/' + "cur_pane_line.png", result)

            if len(bbox_list) != 0:
                horizontal_line = min(bbox_list, key=lambda sublist: sublist[1])
            if playhead is not None and horizontal_line is not None:
                horizontal_line[0] = min(horizontal_line[0], playhead[0])

        # Find all the texts in the panel, filter the timelike text and in blue
        i = 1
        drag_block = []
        remove_chars = '[0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~1.\'`-]+'
        for text in ocr['texts']:
            if match_time_format(text['content']):
                timeline.append({'name': 'timeline-' + str(i), 'rectangle': text['bbox'], 'cur_value': text['content'], 'type': self.action_type + ['typewrite', 'rightClick']})
                timeline_flag = True
                i += 1
            if playhead is not None and horizontal_line is not None:
                if abs(horizontal_line[1] - text['bbox'][1]) < 10: 
                    timeline.append({'name': text['content'] + '|layer', 'rectangle': horizontal_line, 'type': self.action_type + ['doubleClick', 'rightClick', 'dragTo_timeline']})
            
        for text in ocr_cur['texts']:
            if drag_position is not None:
                if is_in_bbox(text['bbox'], drag_position[0]['rectangle']) and re.sub(remove_chars, "", text['content'].lower()) not in ['fx', 'l', 'r', '']:
                    drag_block.append({'name': text['content'], 'rectangle': text['bbox']})
                
        timeline = restore_coordinate(timeline, panel_item['rectangle'])
        drag_block = restore_coordinate(drag_block, panel_item['rectangle'])
        if drag_position is not None:
            drag_position = restore_coordinate(drag_position, panel_item['rectangle'])
        
        return timeline, drag_position, drag_block, timeline_flag

    @staticmethod
    def get_search_bar(panel_item, raw_item):
        # TODO: from meta_data
        all_search_bar = []

        def search_edit_control(item):
            if item['properties']['friendly_class_name'] == 'Edit':
                all_search_bar.append({"name": "Search bar", "rectangle": item['properties']['rectangle'], 'type': ['click', 'typewrite']})

            if len(item['children']) > 0:
                for i in range(len(item['children'])):
                    search_edit_control(item['children'][i])

            return all_search_bar

        return search_edit_control(raw_item)

    @staticmethod
    def get_asset_bar(panel_item):
        if panel_item['name'] not in ['Timeline']:
            return []
        return []

    # @staticmethod
    def get_media_asset(self, panel_item, raw_item, screenshot_path):
        if panel_item['name'] not in ['Program', 'Composition', 'Layer']:
            return []

        try:
            media_asset_box = raw_item['children'][0]['children'][0]['children'][0]['properties']['rectangle']
        except:
            media_asset_box = panel_item['rectangle']

        media_asset = crop_panel(media_asset_box, screenshot_path)
        object_list = self.get_objects(media_asset, media_asset_box)

        # TODO: add guideline
     
     
        return [{'name': 'media_asset',
                 # TODO: check if it is general for other software, only test on PR
                 'rectangle': media_asset_box,
                 'type': self.action_type+['rightClick'],
                 'objects': object_list}]
        # 'objects': object_list}]

    def get_objects(self, media_asset, media_asset_box):
        results = self.yolo_model.predict(source=media_asset, save=False, save_txt=False)

        object_list = []

        for result in results:
            boxes = result.boxes
            names = result.names

            for cls, box in zip(boxes.cls.cpu().numpy().astype(np.uint32), boxes.xyxy.cpu().numpy().astype(np.uint32)):
                cur_children = {
                    'name': names[cls],
                    'rectangle': [int(x) for x in box.tolist()]
                }
                object_list.append(cur_children)

        return restore_coordinate(object_list, media_asset_box)

    @staticmethod
    def get_popup_window(meta_data, window_name):
        panel_item = {'name': window_name, 'rectangle': None}

        # Filter out dictionaries where 'texts' field is empty
        filtered_data = [entry for entry in meta_data if entry['properties']['texts'][0]]

        # Sort the data based on the y-coordinate of the 'rectangle' field (from top to bottom)
        sorted_data_y = sorted(filtered_data, key=lambda x: x['properties']['rectangle'][1])

        elements = []
        current_row = []
        prev_y = None

        for entry in sorted_data_y:
            y = entry['properties']['rectangle'][1]

            # Check if this entry should belong to a new row
            if prev_y is not None and abs(y - prev_y) > 10:
                # Sort the current row from left to right based on the x-coordinate of the 'rectangle' field
                sorted_row_x = sorted(current_row, key=lambda x: x['rectangle'][0])
                elements.append(sorted_row_x)
                current_row = []

            if entry['properties']['friendly_class_name'] in ['MenuItem', 'Button']:
                name = f"{entry['properties']['texts'][0]}"
            else:
                name = f"{entry['properties']['texts'][0]}|{entry['properties']['friendly_class_name']}"

            current_row.append({
                "name": name,
                "rectangle": entry['properties']['rectangle']
            })

            prev_y = y

        if current_row:
            # Sort the last row from left to right before appending it to the matrix
            sorted_row_x = sorted(current_row, key=lambda x: x['rectangle'][0])
            elements.append(sorted_row_x)

        panel_item['elements'] = elements
        panel_item['rectangle'] = find_compact_bounding_box(elements)
        return [panel_item]

    def recognize_panel(self, item, ocr, screenshot_path):
        # TODO: peiran, should be refined with more elegant way
        # first get panel name with ocr
        # Ipython set trace
        # from IPython.core.debugger import Pdb
        # Pdb().set_trace()
        if self.software_name in ['word', 'powerpoint', 'excel']:
            return item['properties']['texts'][0]

        if self.software_name in ['adobe acrobat']:
            if item['properties']['texts'][0] != "AVTabsContainerView":
                self.accessory_number += 1
                return "Accessory" + str(self.accessory_number)

        success, panel_name = self.recognize_panel_with_ocr(item['properties']['rectangle'], ocr['texts'])

        if not success:
            success, panel_name = self.recognize_panel_with_icon(item['properties']['rectangle'], screenshot_path)

        if not success:
            self.accessory_number += 1
            panel_name = 'Accessory' + str(self.accessory_number)
        return panel_name

    def detect_highlight_with_ocr(self, screenshot_path):
        # panel_img = crop_panel(panel_bbox, screenshot_path)
        panel_img = cv2.imread(screenshot_path)
        panel_img = process_image_highlight(panel_img)
        save_path = self.cache_folder + "cur_pane.png"
        cv2.imwrite(save_path, panel_img)

        _, ocr = text_detection(save_path, save_png=False)

        return ocr

    def recognize_panel_with_ocr(self, panel_bbox, ocr_result):
        # TODO: peiran, highlight the panel bbox
        '''
        panel_bbox = [x1, y1, x2, y2]
        ocr_results =
        {'img_shape': (1440, 2560, 3),
         'texts': [{'content': 'Pr', 'bbox': [7, 10, 21, 20]},
                   {'content': 'ZKA', 'bbox': [6, 40, 62, 58]}, ...],}
        '''

        # --- find the topest and leftest text in the panel bbox ---
        # the topest and leftest text in the panel bbox

        def is_same_line(bbox1, bbox2, y_threshold):
            _, y1_min, _, y1_max = bbox1
            _, y2_min, _, y2_max = bbox2

            # Calculate the vertical midpoints of the bounding boxes
            y1_mid = (y1_min + y1_max) / 2
            y2_mid = (y2_min + y2_max) / 2

            # Check if the vertical midpoints are close enough to consider them in the same line
            return abs(y1_mid - y2_mid) <= y_threshold

        top_left_text = None
        y_threshold = 5  # Adjust as needed

        if self.software_name == 'adobe acrobat':
            if '关闭' not in [t['content'] for t in ocr_result]:
                return True, "Document"
            top_threshold = 80  # Adjust as needed
        else:
            top_threshold = 0

        for text in ocr_result:
            # Check if the text is in the panel bounding box
            if is_in_bbox(text['bbox'], panel_bbox):
                # Initialize top_left_text if it is None
                # print("selected text:", text)
                if top_left_text is None:
                    top_left_text = text
                else:
                    # Check if the text is on the same line as the current top_left_text
                    if is_same_line(text['bbox'], top_left_text['bbox'], y_threshold):
                        # If the text is more towards the left, update top_left_text
                        if text['bbox'][0] < top_left_text['bbox'][0]:
                            top_left_text = text
                    else:
                        # print("selected text:", text, top_left_text)
                        # Check if the text is more towards the top
                        if text['bbox'][1] < top_left_text['bbox'][1] - top_threshold:
                            top_left_text = text
                # print("top_left_text: ", top_left_text)

        # print("top_left_text: ", top_left_text)
        # from IPython.core.debugger import Pdb
        # Pdb().set_trace()
        # the ocr could have noise, postprocess the top_left_text by comparing with predefined panel name
        # TODO: update more panel names here
        print("top_left_text: ", top_left_text)
        if top_left_text is None:
            return False, "Accessory"

        text2panel_name = {'效果控件': 'Effect Controls',
                           '效果 控件': 'Effects',
                           '节目': 'Program',
                           '项目': 'Project',
                           '效果': 'Effects',
                           '学习': 'Learn',
                           '基本图形': 'Essential Graphics',
                           '基本声音': 'Essential Sound',
                           'Lumetri 颜色': 'Lumetri Color',
                           'Lumetri 范围': 'Lumetri Scopes',
                           '标记': 'Markers',
                           '历史记录': 'History',
                           '信息': 'Info',
                           '合成': 'Composition',
                           '字符': 'Character',
                           '段落': 'Paragraph',
                           '跟踪器': 'Tracker',
                           '预览': 'Preview',
                           '图层': 'Layer',
                           '对齐': 'Align',
                           '编辑 PDF': 'Edit PDF',
                           '创建 PDF': 'Create PDF',
                           '合并文件': 'Combine Files',
                           '导出 PDF': 'Export PDF',
                           '组织页面': 'Organize Pages',
                           '填写和签名': 'Fill and Sign',
                           '注释': 'Comment',
                           '扫描和OCR': 'Scan and OCR',
                           'Document': 'Document',
                           'Effect Controls': 'Effect Controls',
                           'Effects': 'Effects',
                           'Effects & Presets': 'Effects & Presets',
                           'Program': 'Program',
                           'Project': 'Project',
                           'Learn': 'Learn',
                           'Essential Graphics': 'Essential Graphics',
                           'Essential Sound': 'Essential Sound',
                           'Lumetri Color': 'Lumetri Color',
                           'Lumetri Scopes': 'Lumetri Scopes',
                           'Markers': 'Markers',
                           'History': 'History',
                           'Info': 'Info',
                           'Composition': 'Composition',
                           'Character': 'Character',
                           'Paragraph': 'Paragraph',
                           'Tracker': 'Tracker',
                           'Preview': 'Preview',
                           'Layer': 'Layer',
                           'Audio': 'Audio',
                           'Align': 'Align',
                           }

        # some panel name has more information, e.g. '项目: assistgui', so only keep the first part
        if ':' in top_left_text['content']:
            rough_panel_name = top_left_text['content'].split(':')[0]
        else:
            rough_panel_name = top_left_text['content']  # .split(' ')[0]
        # if self.timeline_name != None and textdistance.levenshtein(rough_panel_name, self.timeline_name) < 2:
        #     return True, "Timeline"

        # compute the editing distance
        min_distance = 100
        min_distance_panel_name = None
        for candidate_panel_name in text2panel_name.keys():
            distance = textdistance.levenshtein(rough_panel_name, candidate_panel_name)
            if distance < min_distance:
                min_distance = distance
                min_distance_panel_name = candidate_panel_name

        # if the distance is too large, cannot recognize the panel with OCR
        if min_distance >= 2:
            return False, "Accessory"
        else:
            if text2panel_name[min_distance_panel_name] == 'Program':
                self.timeline_name = top_left_text['content'].split(':')[1]
            return True, text2panel_name[min_distance_panel_name]

    def recognize_panel_with_icon(self, panel_bbox, screenshot_path):
        # TODO: check if some icons are in the panel
        success = False
        panel_name = None

        panel_img = crop_panel(panel_bbox, screenshot_path)
        button_box = detect_button(panel_img, software_name=self.software_name, panel_name='Tools')

        if len(button_box) > 0:
            success = True
            panel_name = 'Tools'

        return success, panel_name

    def get_software_name(self):
        return self.software_name
