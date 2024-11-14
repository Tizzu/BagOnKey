import json
import os

class Profile:
    def __init__(self, profile_name, tracked_process, layout):
        self.profile_name = profile_name
        self.tracked_process = tracked_process
        self.layout = layout

class ProfileShortcut:
    def __init__(self, name, command):
        self.name = name
        self.command = command

    def to_dict(self):
        return {
            'name': self.name,
            'command': self.command
        }

def load_profile(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        profile_name = data['profileName']
        tracked_process = data.get('tracked_process')
        layout = [ProfileShortcut(**item) for item in data['layout']]
        profile = Profile(profile_name, tracked_process, layout)
    return profile

def save_profile(profile, file_path):
    data = {
        'profileName': profile.profile_name,
        'tracked_process': profile.tracked_process,
        'layout': [item.to_dict() for item in profile.layout]
    }
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def delete_profile(file_path):
    os.remove(file_path)

def rename_profile(new_name, profile, old_file_path, new_file_path):
    os.rename(old_file_path, new_file_path)
    data = {
        'profileName': new_name,
        'layout': [item.to_dict() for item in profile.layout]
    }
    with open(new_file_path, 'w') as file:
        json.dump(data, file, indent=4)



def create_profile(file_path, profile_name):
    data = {
        'profileName': profile_name,
        'tracked_process': "",
        'layout': [{
            "name": "",
            "command": ""
        }] * 18
    }
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)