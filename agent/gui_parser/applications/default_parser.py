from agent.gui_parser.ui_text_detection import text_detection
from agent.gui_parser.utils import *
from agent.gui_parser.gui_parser_base import GUIParserBase


class DefaultParser(GUIParserBase):
    name = "default_parser"
    def __init__(self, cache_folder='.cache/'):
        # judge if the cache folder exists
        super(GUIParserBase, self).__init__()
        self.cache_folder = cache_folder
        self.task_id = get_current_time()

    def __call__(self, meta_data, screenshot_path, software_name=None):
        # only detect text within it
        _, ocr = text_detection(screenshot_path, save_png=False)

        parsed_gui = {}
        for window_name, window_meta_data in meta_data.items():
            if not window_meta_data:
                continue

            parsed_gui[window_name] = self.parse_window(window_meta_data, screenshot_path, ocr, software_name=software_name)

        return parsed_gui

    def parse_window(self, window_meta_data, screenshot_path, ocr, software_name=None):
        main_panel = []
        panel_name = 'Pane'

        for raw_item in window_meta_data:
            if raw_item['properties']['friendly_class_name'] in [panel_name]:
                panel_item = {'name': '',
                              'rectangle': raw_item['properties']['rectangle']}

                # call relevant parser for different panel
                temp = {}
                temp['editing_control'] = self.get_text(panel_item, ocr, screenshot_path)

                # merge all elements at the line
                panel_item['elements'] = self.merge_elements(temp)

                main_panel.append(panel_item)

        return main_panel

