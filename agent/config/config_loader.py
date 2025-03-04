import yaml
import os
current_path = os.path.dirname(os.path.realpath(__file__))

def load_config(file_path='basic.yaml'):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# load the basic configuration under save folder
# get current path

basic_config = load_config(os.path.join(current_path, 'basic.yaml'))
