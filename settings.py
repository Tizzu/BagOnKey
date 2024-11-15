import json
import os

last_selected_profile = ""
tracked_processes = []

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

def load_tracked_processes():
    global tracked_processes
    with open("resources/tracked_processes.json", 'r') as file:
        data = json.load(file)
        tracked_processes = data['tracked_processes']

def save_tracked_processes():
    data = {
        'tracked_processes': tracked_processes
    }
    with open("resources/tracked_processes.json", 'w') as file:
        json.dump(data, file, indent=4)