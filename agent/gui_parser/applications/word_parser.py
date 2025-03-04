from agent.gui_parser.ui_text_detection import text_detection
from agent.gui_parser.utils import *
from agent.gui_parser.gui_parser_base import GUIParserBase
from ultralytics import YOLO


class WordParser(GUIParserBase):
    name = "word_parser"
    def __init__(self, cache_folder='.cache/'):
        # judge if the cache folder exists
        super(GUIParserBase, self).__init__()
        self.cache_folder = cache_folder
        self.task_id = get_current_time()
        self.yolo_model = YOLO("yolov8n-oiv7.pt")
        self.count = 1

    def __call__(self, meta_data, screenshot_path, software_name=None):
        self.software_name = software_name
        self.parsed_gui = {software_name: []}

        # exclude the class name in the list
        self.exclude_class_name_list = ['Custom', 'Menu', 'Pane', 'Toolbar', 'TabControl', 'TreeItem', 'DataItem', 'Hyperlink']

        # self.exclude_class_name_list = []
       
        self.parsed_gui = self.get_panel_uia(meta_data, screenshot_path)
        # Template matching for applications (if applicable)
        
        for panel_item in self.parsed_gui[self.software_name]:
            if panel_item['name'] not in ['Title Bar', 'Navigation Bar']:
                button_box = self.get_button(panel_item, screenshot_path)
                panel_item['elements'] += button_box
                
            if panel_item["name"] in ['Main Content', '工作区', 'Workspace']:
                temp = {}
                panel_crop = crop_panel(panel_item['rectangle'], screenshot_path)
                temp['objects'] = self.get_objects(panel_crop, panel_item['rectangle'])
                panel_item['elements'] += self.merge_elements(temp)
                
        self.postprocess_uia(self.parsed_gui)
        
        return self.parsed_gui
