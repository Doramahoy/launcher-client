import os
import json

minecraft_directory = os.path.join(os.path.dirname(__file__),'..', '..', 'game')

config_file = os.path.join(os.path.dirname(__file__), '..', '..', 'launcher_config.json')
config_file_options = os.path.join(os.path.dirname(__file__), '..', '..', 'minecraft_config.json')
refresh_token_file = os.path.join(minecraft_directory, 'refresh.json')

def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            return json.load(file)
    return {}

def save_config(config):
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, 'w') as file:
        json.dump(config, file, indent=4)
    
def save_config_options(config_options):
    os.makedirs(os.path.dirname(config_file_options), exist_ok=True)
    with open(config_file_options, 'w') as file:
        json.dump(config_options, file, indent=4)

def load_config_options():
    if os.path.exists(config_file_options):
        with open(config_file_options, 'r') as file:
            return json.load(file)
    return {}