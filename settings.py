import json
import os

last_selected_profile = ""

def load_settings():
    global last_selected_profile
    with open("resources/settings.json", 'r') as file:
        data = json.load(file)
        last_selected_profile = data['last_selected_profile']

def save_settings():
    data = {
        'last_selected_profile': last_selected_profile
    }
    with open("resources/settings.json", 'w') as file:
        json.dump(data, file, indent=4)