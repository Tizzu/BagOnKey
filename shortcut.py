import json

class Shortcut:
    def __init__(self, name, description, function):
        self.name = name
        self.description = description
        self.function = str(function)

def load_shortcuts(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        shortcuts = [Shortcut(**item) for item in data]
    return shortcuts

# Load shortcuts from the JSON file
shortcuts = load_shortcuts('shortcuts.json')