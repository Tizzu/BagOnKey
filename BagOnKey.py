import keyboard
import logging
from PIL import Image, ImageDraw
import threading
import win32gui
import win32process
import psutil
import time
import sys, os
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Signal, QObject

import shortcut, profiles, settings, specialFunctions, uiElements

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class DropLabel(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super(DropLabel, self).__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        self.setStyleSheet("border-radius: 17px; border: 2px solid green;")
        e.accept()

    def dragLeaveEvent(self, e):
        self.setStyleSheet("border-radius: 17px; border: 2px solid black;")
        e.accept()

    def dropEvent(self, e):
        self.setStyleSheet("border-radius: 17px; border: 2px solid black;")
        widget = e.source()
        print(f"Button label: {widget.data}")
        # add the shortcut to the current profile
        shortcut = profiles.ProfileShortcut(widget.data, widget.shortcut)
        button_list = list(button_to_key.keys())
        if shortcut.command.startswith("BagOnKey"):
            if shortcut.command.split("|")[1] == "openLink":
                shortcut.name, shortcut.command = specialFunctions.getNameAndLink()
                if shortcut.name == None or shortcut.name == "" or shortcut.command == None or shortcut.command == "":
                    e.accept()
                    return
            elif shortcut.command.split("|")[1] == "customShortcut":
                shortcut.name, shortcut.command = specialFunctions.getCustomShortcut()
                if shortcut.name == None or shortcut.name == "" or shortcut.command == None or shortcut.command == "":
                    e.accept()
                    return
        current_profile.layout[button_list.index(self.objectName())] = shortcut
        save_profile()
        # update the button text
        self.setText(shortcut.name)
        e.accept()
    
    def enterEvent(self, e):
        self.setStyleSheet("border-radius: 17px; border: 2px solid blue;")

    def leaveEvent(self, e):
        self.setStyleSheet("border-radius: 17px; border: 2px solid black;")
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.show_context_menu(event)

    def show_context_menu(self, event):
        context_menu = QtWidgets.QMenu(self)
        action1 = context_menu.addAction("Clear")

        action = context_menu.exec(self.mapToGlobal(event.position().toPoint()))
        if action == action1:
            button_list = list(button_to_key.keys())
            current_profile.layout[button_list.index(self.objectName())] = profiles.ProfileShortcut("", "")
            self.setText("None")
            save_profile()


def save_profile():
    profiles.save_profile(current_profile, f'profiles/{current_profile.profile_name}.json')   

class CustomUiLoader(QUiLoader):
    def createWidget(self, className, parent=None, name=''):
        if (className == 'DropLabel'):
            widget = DropLabel(parent)
            widget.setObjectName(name)
            return widget
        return super().createWidget(className, parent, name)

loader = CustomUiLoader()
app = QtWidgets.QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
app.setWindowIcon(QtGui.QIcon("assets/icon.png"))
dialog = loader.load("resources/interface.ui", None)
dialog.setWindowTitle("BagOnKey")
dialog.setWindowIcon(QtGui.QIcon("assets/icon.png"))
dialog.show()
settings.load_settings()
settings.load_tracked_processes()

profiles_list = dialog.profileList
profiles_list_widget = QtWidgets.QWidget()
profiles_list_content = QtWidgets.QVBoxLayout()

profiles_list_widget.setLayout(profiles_list_content)
profiles_list.setWidget(profiles_list_widget)

process_changer = dialog.processSelectButton
default_checkbox = dialog.defaultProfileCheck

threeKeys = dialog.action3_keys_1_knob
twelveKeys = dialog.action12_keys_2_knobs

def change_layout(setting, save=False):
    if setting == "": # still not set
        setting = "classic"
    if setting == "mini":
        dialog.button4.hide()
        dialog.button5.hide()
        dialog.button6.hide()
        dialog.button7.hide()
        dialog.button8.hide()
        dialog.button9.hide()
        dialog.button10.hide()
        dialog.button11.hide()
        dialog.button12.hide()
        dialog.dial2.hide()
        dialog.knob4.hide()
        dialog.knob5.hide()
        dialog.knob6.hide()
        threeKeys.setChecked(True)
        twelveKeys.setChecked(False)
    elif setting == "classic":
        dialog.button4.show()
        dialog.button5.show()
        dialog.button6.show()
        dialog.button7.show()
        dialog.button8.show()
        dialog.button9.show()
        dialog.button10.show()
        dialog.button11.show()
        dialog.button12.show()
        dialog.dial2.show()
        dialog.knob4.show()
        dialog.knob5.show()
        dialog.knob6.show()
        threeKeys.setChecked(False)
        twelveKeys.setChecked(True)
    if save:
        settings.selected_layout = setting
        settings.save_settings()

threeKeys.triggered.connect(lambda: change_layout("mini", True))
twelveKeys.triggered.connect(lambda: change_layout("classic", True))
change_layout(settings.selected_layout)

# for each profile in the profiles folder, add it to the list

def process_label_change(process_name):
    process_changer.setText(process_name + "\n(Click to change)")

def reload_buttons():
    # clean the layout
    for i in reversed(range(profiles_list_content.count())):
        profiles_list_content.itemAt(i).widget().deleteLater()
    for profile in os.listdir("profiles"):
        profile_button = QtWidgets.QPushButton(profile.split(".")[0])
        if (profile.split(".")[0] == current_profile.profile_name):
            profile_button.setStyleSheet("border-radius: 17px; border: 3px solid green; padding: 5px;")
        else:
            profile_button.setStyleSheet("border-radius: 17px; border: 2px solid black; padding: 5px;")
        def on_profile_click(profile_name):
            global current_profile
            current_profile = load_profile(profile_name)
        profile_button.clicked.connect(lambda _, pn = profile.split(".")[0]: on_profile_click(pn))
        profiles_list_content.addWidget(profile_button)

key_to_button = {
    ('f13', 'key'): dialog.button1,
    ('f14', 'key'): dialog.button2,
    ('f15', 'key'): dialog.button3,
    ('f16', 'key'): dialog.button4,
    ('f17', 'key'): dialog.button5,
    ('f18', 'key'): dialog.button6,
    ('f19', 'key'): dialog.button7,
    ('f20', 'key'): dialog.button8,
    ('f21', 'key'): dialog.button9,
    ('f22', 'key'): dialog.button10,
    ('f23', 'key'): dialog.button11,
    ('f24', 'key'): dialog.button12,
    ('alt+shift+1', 'shortcut'): dialog.knob1,
    ('alt+shift+2', 'shortcut'): dialog.knob2,
    ('alt+shift+3', 'shortcut'): dialog.knob3,
    ('alt+shift+4', 'shortcut'): dialog.knob4,
    ('alt+shift+5', 'shortcut'): dialog.knob5,
    ('alt+shift+6', 'shortcut'): dialog.knob6
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
    "knob1": 'alt+shift+1',
    "knob2": 'alt+shift+2',
    "knob3": 'alt+shift+3',
    "knob4": 'alt+shift+4',
    "knob5": 'alt+shift+5',
    "knob6": 'alt+shift+6'
}

class PopupNotification(QtWidgets.QWidget):
    def __init__(self, profile_name, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | 
            QtCore.Qt.FramelessWindowHint | 
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)

        global dial_position
        layout = QtWidgets.QHBoxLayout(self)

        # Add icon to the popup
        icon_label = QtWidgets.QLabel()
        icon = QtGui.QIcon("assets/icon.png")  # Replace with the path to your icon
        icon_pixmap = icon.pixmap(32, 32)  # Adjust the size as needed
        icon_label.setPixmap(icon_pixmap)
        layout.addWidget(icon_label)

        label = QtWidgets.QLabel(f"Profile: {profile_name}")
        layout.addWidget(label)

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 255);
                color: white;
            }
            QLabel {
                font-size: 16px;
            }
        """)

        self.adjustSize()
        self.move_to_corner()

    def move_to_corner(self):
        # Get mouse cursor position
        cursor_pos = QtGui.QCursor.pos()
        # Identify the screen at cursor position
        screen = QtGui.QGuiApplication.screenAt(cursor_pos)
        if screen:
            # Get available geometry of the screen
            screen_geometry = screen.availableGeometry()
            x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
            y = screen_geometry.y() + screen_geometry.height() - self.height() - 50
            self.move(x, y)
        else:
            # Fallback to primary screen if no screen is found
            screen_geometry = QtGui.QGuiApplication.primaryScreen().availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = screen_geometry.height() - self.height() - 50
            self.move(x, y)

    def show_notification(self, duration=2000):
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | 
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.activateWindow()
        self.raise_()
        self.show()
        QtCore.QTimer.singleShot(duration, self.close)



# Add a global variable to store the current active notification
current_notification = None

def show_profile_notification(profile_name):
    global current_notification
    # Close the existing notification if it exists
    if current_notification:
        current_notification.close()
    
    # Create the PopupNotification instance
    current_notification = PopupNotification(profile_name)
    # Show the notification
    current_notification.show_notification()

def clear_current_notification():
    global current_notification
    current_notification = None

def load_profile(profile_name):
    name = profile_name
    profile = profiles.load_profile(f'profiles/{name}.json')
    if profile is None:
        profile = profiles.load_profile("profiles/default.json") 
        name = "default"
    if name != settings.last_selected_profile:
        settings.last_selected_profile = name
        settings.save_settings()
        show_profile_notification(name)  
    # for each dialog button, set the text to the corresponding shortcut name
    for i, button in enumerate(key_to_button.values()):
        if profile.layout[i].name == "":
            button.setText("None")
        else: 
            button.setText(profile.layout[i].name)
    # get the profiles list and make a green border to the selected profile, and a black border to the others
    for i in range(profiles_list_content.count()):
        if profiles_list_content.itemAt(i).widget().text() == name:
            profiles_list_content.itemAt(i).widget().setStyleSheet("border-radius: 17px; border: 2px solid green; padding: 5px;")
        else:
            profiles_list_content.itemAt(i).widget().setStyleSheet("border-radius: 17px; border: 2px solid black; padding: 5px;")
    # find the process name for the profile --> tracked_processes (profile_name, process_name)
    for profile_name, tracked_process in settings.tracked_processes:
        if profile_name == name:
            process_label_change(tracked_process)
            break
    default_checkbox.setChecked(name == settings.default_profile)
    return profile

# Initial profile load
current_profile = load_profile(settings.last_selected_profile)

def on_checkbox_change():
    if default_checkbox.isChecked():
        settings.default_profile = current_profile.profile_name
        settings.save_settings()
    else:
        settings.default_profile = ""
        settings.save_settings()

default_checkbox.clicked.connect(on_checkbox_change)

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
    except ValueError:
        return "Unknown"

last_process = None

def on_process_change(process_name):
    global current_profile
    found = False
    for profile_name, tracked_process in settings.tracked_processes:
        if tracked_process == process_name:
            current_profile = load_profile(profile_name)
            found = True
            break
    if not found and settings.default_profile != "":
        current_profile = load_profile(settings.default_profile)

class ProcessMonitor(QObject):
    process_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.last_process = None

    def monitor_process(self):
        while True:
            process_name = get_foreground_process_name()
            if process_name != self.last_process:
                logging.info(f'Foreground process changed to {process_name}')
                self.last_process = process_name
                self.process_changed.emit(process_name)
            time.sleep(0.5)  # Adjust the interval as needed

process_monitor = ProcessMonitor()
process_monitor.process_changed.connect(on_process_change)

monitor_thread = threading.Thread(target=process_monitor.monitor_process, daemon=True)
monitor_thread.start()

isPressed = False

def on_button_click(event):
    isShortcut = False
    button_list = list(button_to_key.values())
    if isinstance(event, str):
        isShortcut = True
    process_name = get_foreground_process_name()
    if not isShortcut:
        logging.info(f'Key {event.name.upper()} pressed in process {process_name}')
        command = current_profile.layout[button_list.index(event.name)].command
    else:
        logging.info(f'Shortcut {event} pressed in process {process_name}')
        command = current_profile.layout[button_list.index(event)].command
    
    if (command != ""):
        if (command.startswith("BagOnKey")):
            if (command.split("|")[1] == "openLink"):
                specialFunctions.openLink(command.split("|")[2])
        else:
            keyboard.press_and_release(command)


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

class DragButton(QtWidgets.QPushButton):
    def __init__(self, label, shortcut, *args, **kwargs):
        super().__init__(label, *args, **kwargs)
        self.data = label
        self.shortcut = shortcut
        self.setStyleSheet("border-radius: 17px; border: 1px solid black; padding: 5px;")

    def mouseMoveEvent(self, e):
        if e.buttons() == QtCore.Qt.MouseButton.LeftButton:
            drag = QtGui.QDrag(self)
            mime = QtCore.QMimeData()
            drag.setMimeData(mime)

            pixmap = QtGui.QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec(QtCore.Qt.DropAction.MoveAction)
            self.show() 

def delete_dialog(profile_name):
    delete_dialog = QtWidgets.QDialog()
    delete_dialog.setWindowTitle("Delete Profile")
    delete_dialog.setWindowIcon(QtGui.QIcon("assets/icon.png"))
    delete_dialog.resize(200, 100)
    layout = QtWidgets.QVBoxLayout()
    delete_dialog.setLayout(layout)
    # if name is default say it's not possible to delete
    if profile_name == "default":
        label = QtWidgets.QLabel("You cannot delete the default profile")
        layout.addWidget(label)
        yes_button_sad = QtWidgets.QPushButton("Ok :(")
        yes_button_sad.clicked.connect(delete_dialog.reject)
        layout.addWidget(yes_button_sad)
        delete_dialog.exec()
        return
    label = QtWidgets.QLabel(f"Are you sure you want to delete the profile {profile_name}?")
    yes_button = QtWidgets.QPushButton("Yes")
    no_button = QtWidgets.QPushButton("No")
    
    layout.addWidget(label)
    layout.addWidget(yes_button)
    layout.addWidget(no_button)
    
    def on_yes_clicked():
        global current_profile
        profiles.delete_profile(f'profiles/{profile_name}.json')
        current_profile = load_profile("default")
        settings.tracked_processes = [x for x in settings.tracked_processes if x[0] != profile_name]
        settings.save_tracked_processes()
        reload_buttons()
        delete_dialog.accept()
    
    def on_no_clicked():
        delete_dialog.reject()
    
    yes_button.clicked.connect(on_yes_clicked)
    #if the enter key is pressed, the yes button is clicked
    yes_button.setAutoDefault(True)
    no_button.clicked.connect(on_no_clicked)
    
    delete_dialog.exec()

def create_profile():
    create_dialog = QtWidgets.QDialog()
    create_dialog.setWindowTitle("Create Profile")
    create_dialog.setWindowIcon(QtGui.QIcon("assets/icon.png"))
    create_dialog.resize(200, 100)
    layout = QtWidgets.QVBoxLayout()
    create_dialog.setLayout(layout)
    label = QtWidgets.QLabel("Enter the name of the profile")
    input_field = QtWidgets.QLineEdit()
    create_button = QtWidgets.QPushButton("Create")
    cancel_button = QtWidgets.QPushButton("Cancel")
    
    layout.addWidget(label)
    layout.addWidget(input_field)
    layout.addWidget(create_button)
    
    def on_create_clicked():
        global current_profile
        profile_name = input_field.text()
        profiles.create_profile(f'profiles/{profile_name}.json', profile_name)
        current_profile = load_profile(profile_name)
        settings.tracked_processes.append([profile_name, "None"])
        settings.save_tracked_processes()
        reload_buttons()
        create_dialog.accept()
    
    create_button.clicked.connect(on_create_clicked)
    create_button.setAutoDefault(True)
    cancel_button.clicked.connect(create_dialog.reject)
    
    create_dialog.exec()

def rename_profile(profile_name):
    rename_dialog = QtWidgets.QDialog()
    rename_dialog.setWindowTitle("Rename Profile")
    rename_dialog.setWindowIcon(QtGui.QIcon("assets/icon.png"))
    rename_dialog.resize(200, 100)
    layout = QtWidgets.QVBoxLayout()
    rename_dialog.setLayout(layout)
    if profile_name == "default":
        label = QtWidgets.QLabel("You cannot rename the default profile")
        layout.addWidget(label)
        yes_button_sad = QtWidgets.QPushButton("Ok :(")
        yes_button_sad.clicked.connect(rename_dialog.reject)
        layout.addWidget(yes_button_sad)
        rename_dialog.exec()
        return
    label = QtWidgets.QLabel("Enter the new name of the profile")
    input_field = QtWidgets.QLineEdit()
    # add the current profile name to the input field
    input_field.setText(profile_name)
    rename_button = QtWidgets.QPushButton("Rename")
    cancel_button = QtWidgets.QPushButton("Cancel")
    
    layout.addWidget(label)
    layout.addWidget(input_field)
    layout.addWidget(rename_button)
    
    def on_rename_clicked():
        global current_profile
        new_profile_name = input_field.text()
        profiles.rename_profile(new_profile_name, current_profile, f'profiles/{profile_name}.json', f'profiles/{new_profile_name}.json')
        current_profile = load_profile(new_profile_name)
        settings.tracked_processes = [x for x in settings.tracked_processes if x[0] != profile_name]
        settings.tracked_processes.append([new_profile_name, "None"])
        settings.save_tracked_processes()
        reload_buttons()
        rename_dialog.accept()
    
    rename_button.clicked.connect(on_rename_clicked)
    rename_button.setAutoDefault(True)
    cancel_button.clicked.connect(rename_dialog.reject)
    
    rename_dialog.exec()

scroll_area = dialog.ideasList
content_widget = QtWidgets.QWidget()
content_layout = QtWidgets.QVBoxLayout()

description_scroll_area = dialog.description
description_widget = QtWidgets.QWidget()
description_layout = QtWidgets.QVBoxLayout()

for i in shortcut.shortcuts:
    button = DragButton(i.name, i.function)
    button.clicked.connect(lambda _, desc=i.description: refresh_description(desc))
    content_layout.addWidget(button)

content_widget.setLayout(content_layout)
scroll_area.setWidget(content_widget)
description_widget.setLayout(description_layout)
description_scroll_area.setWidget(description_widget)

exit_menu_bar = dialog.actionExit
exit_menu_bar.triggered.connect(app.quit)
delete_profile_menu = dialog.actionDelete
delete_profile_menu.triggered.connect(lambda: delete_dialog(current_profile.profile_name))

create_profile_menu = dialog.actionAdd_new_profile
create_profile_menu.triggered.connect(lambda: create_profile())

rename_profile_menu = dialog.actionRename
rename_profile_menu.triggered.connect(lambda: rename_profile(current_profile.profile_name))


def extractProcessName(file_path):
    return os.path.basename(file_path)

def showFileDialog(self):
    global process_changer
    if current_profile.profile_name == "default":
        no_dialog = QtWidgets.QDialog()
        no_dialog.setWindowTitle("Rename Profile")
        no_dialog.setWindowIcon(QtGui.QIcon("assets/icon.png"))
        no_dialog.resize(200, 100)
        layout = QtWidgets.QVBoxLayout()
        no_dialog.setLayout(layout)
        label = QtWidgets.QLabel("You cannot change the process of the default profile")
        layout.addWidget(label)
        yes_button_sad = QtWidgets.QPushButton("Ok :(")
        yes_button_sad.clicked.connect(no_dialog.reject)
        layout.addWidget(yes_button_sad)
        no_dialog.exec()
        # show a dialog saying you can't change the process
        return
    options = QtWidgets.QFileDialog.Option(QtWidgets.QFileDialog.Option.DontUseNativeDialog)
    file_filter = "Executable Files (*.exe)"
    file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", file_filter, options=options)
    if file_name:
        process_name = extractProcessName(file_name)
        # this process name will be the one to be used for tracking the process when the foreground process changes
        settings.tracked_processes = [x for x in settings.tracked_processes if x[0] != current_profile.profile_name]
        settings.tracked_processes.append([current_profile.profile_name, process_name])
        process_label_change(process_name)
        settings.save_tracked_processes()

process_changer.clicked.connect(lambda: showFileDialog(dialog))
process_cleaner = dialog.clearSelection

def clearProcessName():
    process_label_change("None")
    settings.tracked_processes = [x for x in settings.tracked_processes if x[0] != current_profile.profile_name]
    settings.tracked_processes.append([current_profile.profile_name, "None"])
    settings.save_tracked_processes()

process_cleaner.clicked.connect(lambda: clearProcessName())

about_menu = dialog.actionAbout_BagOnKey
about_menu.triggered.connect(uiElements.show_about_dialog)

help_on_configuring = dialog.actionUse_this_tool_with_your_keyboard
help_on_configuring.triggered.connect(uiElements.show_help_dialog)

dialog.show()
reload_buttons()

# Set up keyboard event handlers
for key, type in key_to_button.keys():
    if type == 'key':
        keyboard.on_release_key(key, on_button_click, suppress=True)
    else:
        keyboard.add_hotkey(key, on_button_click, args=(key,), suppress=True)

app.exec()