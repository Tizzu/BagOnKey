import json

class Profile:
    def __init__(self, profile_name, layout):
        self.profile_name = profile_name
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
        layout = [ProfileShortcut(**item) for item in data['layout']]
        profile = Profile(profile_name, layout)
    return profile

def save_profile(profile, file_path):
    data = {
        'profileName': profile.profile_name,
        'layout': [item.to_dict() for item in profile.layout]
    }
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)