import keyboard
import logging
import pystray
from PIL import Image, ImageDraw
import threading
import os
import win32gui
import win32process
import psutil
import time
import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtUiTools import QUiLoader

import shortcut, profiles

class DropLabel(QtWidgets.QGraphicsView):
    def __init__(self, *args, **kwargs):
        super(DropLabel, self).__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        self.setStyleSheet("border: 3px solid green;")
        e.accept()

    def dragLeaveEvent(self, e):
        self.setStyleSheet("border: 3px solid black;")
        e.accept()

    def dropEvent(self, e):
        self.setStyleSheet("border: 3px solid black;")
        widget = e.source()
        print(f"Button label: {widget.data}")
        # add the shortcut to the current profile
        current_profile[button_to_array_index.get(self.objectName())] = (widget.data, widget.shortcut)
        print(f"Current profile: {current_profile}")
        # update the button text
        e.accept()

class CustomUiLoader(QUiLoader):
    def createWidget(self, className, parent=None, name=''):
        if className == 'DropLabel':
            widget = DropLabel(parent)
            widget.setObjectName(name)
            return widget
        return super().createWidget(className, parent, name)

loader = CustomUiLoader()
app = QtWidgets.QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
dialog = loader.load("resources/interface.ui", None)
dialog.setWindowTitle("BagOnKey")
dialog.setWindowIcon(QtGui.QIcon("assets/icon.png"))
dialog.show()

current_profile = [("", "")] * 12
# current_profile = profiles.load_profile('profiles/default.json') # Load the default profile

key_to_button = {
    'f13': dialog.button1,
    'f14': dialog.button2,
    'f15': dialog.button3,
    'f16': dialog.button4,
    'f17': dialog.button5,
    'f18': dialog.button6,
    'f19': dialog.button7,
    'f20': dialog.button8,
    'f21': dialog.button9,
    'f22': dialog.button10,
    'f23': dialog.button11,
    'f24': dialog.button12,
    # Add more keys once the knobs are defined
}

button_to_key = {
    "button1": 'f13',
    "button2": 'f14',
    "button3": 'f15',
    "button4": 'f16',
    "button5": 'f17',
    "button6": 'f18',
    "button7": 'f19',
    "button8": 'f20',
    "button9": 'f21',
    "button10": 'f22',
    "button11": 'f23',
    "button12": 'f24',
}

button_to_array_index = {
    "button1": 0,
    "button2": 1,
    "button3": 2,
    "button4": 3,
    "button5": 4,
    "button6": 5,
    "button7": 6,
    "button8": 7,
    "button9": 8,
    "button10": 9,
    "button11": 10,
    "button12": 11,
}


key_to_array_index = {
    'f13': 0,
    'f14': 1,
    'f15': 2,
    'f16': 3,
    'f17': 4,
    'f18': 5,
    'f19': 6,
    'f20': 7,
    'f21': 8,
    'f22': 9,
    'f23': 10,
    'f24': 11,
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def create_icon():
    image = Image.open("assets/icon.png")
    ImageDraw.Draw(image)
    return image

def get_foreground_process_name():
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        process = psutil.Process(pid)
        return process.name()
    except psutil.Error:
        return "Unknown"

last_process = None

def monitor_foreground_process_thread():
    global last_process
    while True:
        process_name = get_foreground_process_name()
        if process_name != last_process:
            logging.info(f'Foreground process changed to {process_name}')
            last_process = process_name
        time.sleep(0.5)  # Adjust the interval as needed

def on_button_click(event):
    button = key_to_button.get(event.name)
    process_name = get_foreground_process_name()
    logging.info(f'Key {event.name.upper()} pressed in process {process_name}')
    command = current_profile[key_to_array_index.get(event.name)][1]
    if button:
            button.setStyleSheet("border: 3px solid red;")
    if (command != ""):
        keyboard.press_and_release(command)


def on_button_release(event):
    button = key_to_button.get(event.name)
    if button:
        button.setStyleSheet("border: 3px solid black;")

def on_dialog_close(event):
    dialog.hide()
    event.ignore()

dialog.closeEvent = on_dialog_close

# Create the system tray icon
tray_icon = QtWidgets.QSystemTrayIcon(QtGui.QIcon("assets/icon.png"))
tray_icon.setToolTip("BagOnKey")

# Create the menu for the tray icon and keep a reference to it
tray_menu = QtWidgets.QMenu(dialog)
open_action = tray_menu.addAction("Open")
exit_action = tray_menu.addAction("Exit")
tray_icon.setContextMenu(tray_menu)

# Connect the actions
open_action.triggered.connect(dialog.show)
exit_action.triggered.connect(app.quit)

# Handle tray icon activation
def on_tray_icon_activated(reason):
    if reason == QtWidgets.QSystemTrayIcon.Trigger:
        dialog.show()

tray_icon.activated.connect(on_tray_icon_activated)
tray_icon.show()

def refresh_description(desc):
    #safely remove all widgets from the layout using deleteLater
    for i in reversed(range(description_layout.count())):
        description_layout.itemAt(i).widget().deleteLater()
    description_layout.addWidget(QtWidgets.QLabel(desc))


# Start the background thread
threading.Thread(target=monitor_foreground_process_thread, daemon=True).start()

class DragButton(QtWidgets.QPushButton):
    def __init__(self, label, shortcut, *args, **kwargs):
        super().__init__(label, *args, **kwargs)
        self.data = label
        self.shortcut = shortcut

    def mouseMoveEvent(self, e):
        if e.buttons() == QtCore.Qt.MouseButton.LeftButton:
            drag = QtGui.QDrag(self)
            mime = QtCore.QMimeData()
            drag.setMimeData(mime)
            self.setContentsMargins(25, 5, 25, 5)
            self.setStyleSheet("border: 1px solid black;")

            pixmap = QtGui.QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec(QtCore.Qt.DropAction.MoveAction)
            self.show() 

# Show the dialog and start the application event loop
scroll_area = dialog.ideasList
content_widget = QtWidgets.QWidget()
content_layout = QtWidgets.QVBoxLayout()

description_scroll_area = dialog.description
description_widget = QtWidgets.QWidget()
description_layout = QtWidgets.QVBoxLayout()

for i in shortcut.shortcuts:
    button = DragButton(i.name, i.function)
    # log the function of the button
    button.clicked.connect(lambda _, desc=i.description: refresh_description(desc))
    content_layout.addWidget(button)
    

content_widget.setLayout(content_layout)
scroll_area.setWidget(content_widget)
description_widget.setLayout(description_layout)
description_scroll_area.setWidget(description_widget)
dialog.show()

# Set up keyboard event handlers
for key in key_to_button.keys():
    keyboard.on_press_key(key, on_button_click)
    keyboard.on_release_key(key, on_button_release)

app.exec()