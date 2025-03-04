from agent.gui_parser.ui_text_detection import text_detection
from agent.gui_parser.utils import *
from agent.gui_parser.gui_parser_base import GUIParserBase


class WebParser(GUIParserBase):
    name = "web_parser"
    def __init__(self, cache_folder='.cache/'):
        # judge if the cache folder exists
        super(GUIParserBase, self).__init__()
        self.cache_folder = cache_folder
        self.task_id = get_current_time()
        self.count = 1

    def __call__(self, meta_data, screenshot_path, software_name=None):
        self.software_name = software_name
        self.parsed_gui = {software_name: []}

        main_name = list(meta_data.keys())[0]
        if any(keyword in main_name for keyword in ['哔哩哔哩', 'bilibili', '腾讯视频']):
            self.software_name = 'web video'
            self.exclude_class_name_list = ['GroupBox', 'ListBox', 'ListItem', 'Custom', 'Menu', 'Pane', 'Toolbar', 'TabControl', 'TreeItem', 'DataItem']
        elif any(keyword in main_name.lower() for keyword in ['amazon', 'shopee', 'powerpoint']): # '淘宝' 不使用OCR效果更好
            if self.software_name == 'powerpoint':
                self.exclude_class_name_list = ['Custom', 'Menu', 'Pane', 'Toolbar', 'TabControl', 'TreeItem', 'DataItem', 'Hyperlink']
            else:
                self.software_name = 'web ocr'
                self.exclude_class_name_list = ['GroupBox', 'ListBox', 'ListItem', 'Custom', 'Menu', 'Pane', 'Toolbar', 'TabControl', 'TreeItem', 'DataItem', 'Hyperlink']
            
            self.parsed_gui = self.get_panel_uia_ocr(meta_data, screenshot_path)
            _, ocr = text_detection(screenshot_path, save_png=False)

            self.postprocess_uia(self.parsed_gui)

            for panel_item in self.parsed_gui[self.software_name]:
                if panel_item["name"] in ['Main Content', '工作区', 'Workspace']:
                    temp = {}
                    temp['editing_control'] = self.get_text(panel_item, ocr, screenshot_path, type='web')
                    panel_item['elements'] += self.merge_elements(temp)

            return self.parsed_gui
        
        elif any(keyword in main_name.lower() for keyword in ['word', 'excel']):
            self.exclude_class_name_list = ['Custom', 'Menu', 'Pane', 'Toolbar', 'TabControl', 'TreeItem', 'DataItem', 'Hyperlink']
        elif any(keyword in main_name.lower() for keyword in ['bbc news']):
            self.exclude_class_name_list = ['GroupBox', 'ListBox', 'ListItem', 'Custom', 'Menu', 'Pane', 'Toolbar', 'TabControl', 'TreeItem', 'DataItem',]
        else:
            self.exclude_class_name_list = ['GroupBox', 'ListBox', 'ListItem', 'Custom', 'Menu', 'Pane', 'Toolbar', 'TabControl', 'TreeItem', 'DataItem', 'Hyperlink']
        
        
        self.parsed_gui = self.get_panel_uia(meta_data, screenshot_path)
        # Template matching for these applications
        for panel_item in self.parsed_gui[self.software_name]:
            if panel_item['name'] not in ['Title Bar', 'Navigation Bar']:
                button_box = self.get_button(panel_item, screenshot_path)
                panel_item['elements'] += button_box

        self.postprocess_uia(self.parsed_gui)
        
        return self.parsed_gui


    # def get_panel_uia_ocr(self, control_info_list, screenshot_path):

    #     def recurse_controls(control_info, dialog_components, type='normal', depth = 1):

    #         children = control_info['children']
    #         if len(children) == 0:
    #             return

    #         for child_control in children:
    #             child_properties = child_control['properties']
    #             child_friendly_class_name = child_properties['friendly_class_name']
    #             child_properties_name = ''

    #             # Get the feasible name of the child control
    #             if len(child_properties['texts']) == 0:
    #                 child_properties_name = ''  
    #             elif isinstance(child_properties['texts'][0],list) and len(child_properties['texts']) != 0:
    #                 result = []
    #                 for item in child_properties['texts']:
    #                     if isinstance(item[0], str):
    #                         result.append(''.join(item))
    #                 child_properties_name = ''.join(result)
    #             else:
    #                 child_properties_name = child_properties['texts'][0]

    #             # Get the search bar
    #             if child_friendly_class_name in ['Edit', 'ComboBox'] and (child_properties_name == '' or 'search' not in child_properties_name.lower()):
    #                     child_properties_name = 'Search Bar'

    #             conditions = {
    #                 'static': (
    #                     child_friendly_class_name == 'CheckBox' and
    #                     child_properties_name not in ['', '"'] and
    #                     not all(element == 0 for element in child_properties['rectangle']),
    #                     dialog_components['rectangle']
    #                 ),
    #                 'normal': (
    #                     'search' in child_properties_name.lower() and
    #                     child_friendly_class_name == 'GroupBox' or
    #                     (child_friendly_class_name not in self.exclude_class_name_list or
    #                     len(child_control['children']) == 0) and
    #                     child_properties_name not in ['', '"'] and
    #                     not all(element == 0 for element in child_properties['rectangle']),
    #                     dialog_components['rectangle']
    #                 )
    #             }

    #             if conditions.get(type, (False, None))[0]:
    #                 left, top, right, bottom = child_properties['rectangle']
    #                 left_bound, top_bound, right_bound, bottom_bound = dialog_components['rectangle']
                    
    #                 if self.software_name not in ['word', 'excel', 'powerpoint']:
    #                     if left < left_bound:
    #                         child_properties['rectangle'][0] = left_bound
    #                     if top < top_bound:
    #                         child_properties['rectangle'][1] = top_bound
    #                     if right > right_bound:
    #                         child_properties['rectangle'][2] = right_bound
    #                     if bottom > bottom_bound:
    #                         child_properties['rectangle'][3] = bottom_bound

    #                 if not (child_properties['rectangle'][0] >= child_properties['rectangle'][2] or child_properties['rectangle'][1] >= child_properties['rectangle'][3]):
    #                     # remove unseen characters
    #                     child_properties_name = child_properties_name.replace('\u200b', '')

    #                     dialog_components['elements'].append({
    #                         'name': child_properties_name,
    #                         'rectangle': child_properties['rectangle'],
    #                         'class_name': child_friendly_class_name,
    #                         'type': ['Click', 'rightClick'],
    #                         'depth': depth + '-' + str(self.count)
    #                     })

    #                     self.count += 1

    #             recurse_controls(child_control, dialog_components, type, depth)

        
    #     main_name = list(control_info_list.keys())[0]
    #     dialog_components = {self.software_name: []}

    #     # Check if the friendly_class_name
    #     for control_info in control_info_list[main_name]:

    #         if control_info['properties']['friendly_class_name'] in ['Dialog', 'Pane', 'GroupBox', 'TitleBar', 'Menu', 'Document', 'ListBox'] and len(control_info['children']) != 0:
    #             # Append texts and rectangle to the Dialog components
    #             # if all(element == 0 for element in control_info['properties']['rectangle']):
    #             #     continue

    #             # Main panel name rules
    #             if control_info['properties']['texts'][0] == '':
    #                 if control_info['properties']['friendly_class_name'] == 'TitleBar':
    #                     control_name = 'Title Bar'

    #                 if control_info['properties']['friendly_class_name'] == 'Document':
    #                     control_name = 'Main Content'
                        
    #                 if control_info['properties']['friendly_class_name'] == 'Pane':
    #                     if self.software_name in ['web', 'web video', 'web ocr', 'powerpoint']:
    #                         control_name = 'Navigation Bar'
    #                     else:
    #                         control_name = 'Main Content'
    #             else:
    #                 if control_info['properties']['friendly_class_name'] == 'Document' and self.software_name in ['web', 'web video', 'web ocr', 'powerpoint']:
    #                     control_name = 'Main Content'
    #                     if 'Outlook' in main_name and 'Mail' in main_name:
    #                         original_value = dialog_components.pop(self.software_name)
    #                         self.software_name = 'Outlook'
    #                         dialog_components['Outlook'] = original_value
    #                 else:
    #                     control_name = control_info['properties']['texts'][0]


    #             self.count = 1
    #             dialog_components[self.software_name].append({
    #                 'name': control_name,
    #                 'rectangle': control_info['properties']['rectangle'],
    #                 'class_name': control_info['properties']['friendly_class_name'],
    #                 'depth': '1',
    #                 'elements': []
    #             })

    #             # Process children of the Dialog
    #             if control_name == 'Main Content':
    #                 recurse_controls(control_info, dialog_components[self.software_name][-1], type='static', depth = '1')
    #             else:
    #                 recurse_controls(control_info, dialog_components[self.software_name][-1], depth = '1')

    #     return dialog_components

