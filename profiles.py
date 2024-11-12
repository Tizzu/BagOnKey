import json

class Profile:
    def __init__(self, profile_name, layout):
        self.profile_name = profile_name
        self.layout = layout

class ProfileShortcut:
    def __init__(self, name, command):
        self.name = name
        self.command = command

def load_profile(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        profile_name = data['profileName']
        layout = [ProfileShortcut(**item) for item in data['layout']]
        profile = Profile(profile_name, layout)
    return profile