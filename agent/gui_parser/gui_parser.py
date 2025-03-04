import importlib
from agent.base_module import BaseModule
from agent.gui_parser.utils import *

CYAN = "\033[96m"
END = "\033[0m"


class GUIParser(BaseModule):
    name = "gui_parser"
    description = """
This tool can extract the information of screenshot.
Invoke command: (query, visual[i])
:param query -> str, specific command. visual[i] -> image, the latest screenshot.
"""

    def __init__(self, cache_folder=".cache/"):
        # judge if the cache folder exists
        super(GUIParser, self).__init__()
        self.cache_folder = cache_folder
        self.task_id = get_current_time()
        # YOLOv8 model that can detect 600 classes
        # self.yolo_model = self.build_model("yolov8")
        self.parsers = {}
        self.temperature = 0
        self.load_parsers_from_config(os.path.abspath(os.path.join(os.path.dirname(__file__), 'applications.config')))

    def load_parsers_from_config(self, config_file):
        print("load parsers from config")
        prefix = "agent.gui_parser.applications."
        with open(config_file, "r", encoding="utf-8") as file:
            for line in file:
                software_name, parser_class = line.strip().split(",")
                module_name, class_name = parser_class.rsplit(".", 1)
                module = importlib.import_module(prefix + module_name)
                parser = getattr(module, class_name)()
                self.register_parser(software_name, parser)

    def register_parser(self, software_name, parser):
        self.parsers[software_name] = parser

    def _run(self, software_name, meta_data, screenshot_path):
        print(self.parsers)
        parser = self.get_parser(software_name)
        print(f"{CYAN}parser.name: ", parser.name, f"{END}")
        return parser(meta_data, screenshot_path, software_name)

    def process_software_name(self, software_name):
        return software_name

    def get_parser(self, software_name):
        software_name = self.process_software_name(software_name)
        software_name = software_name.lower()
        return self.parsers[software_name]
