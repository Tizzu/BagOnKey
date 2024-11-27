import keyboard
import logging
from PIL import Image, ImageDraw
import threading
import win32gui, win32process, win32api, win32event, winerror
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
        app_instance = QtWidgets.QApplication.instance()
        button_list = list(app_instance.button_to_key.keys())
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
        app_instance.current_profile.layout[button_list.index(self.objectName())] = shortcut
        app_instance.save_profile()
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
            app_instance = QtWidgets.QApplication.instance()
            button_list = list(app_instance.button_to_key.keys())
            app_instance.current_profile.layout[button_list.index(self.objectName())] = profiles.ProfileShortcut("", "")
            self.setText("None")
            app_instance.save_profile()


class BagOnKeyApp(QtWidgets.QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        # Initialize mutex
        mutex = win32event.CreateMutex(None, False, 'BagOnKeyMutex')
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            sys.exit(0)
        # Initialize UI loader and load the interface
        self.loader = CustomUiLoader()
        self.setQuitOnLastWindowClosed(False)
        self.setWindowIcon(QtGui.QIcon("assets/icon.png"))
        self.dialog = self.loader.load("resources/interface.ui", None)
        self.dialog.setWindowTitle("BagOnKey")
        self.dialog.setWindowIcon(QtGui.QIcon("assets/icon.png"))
        self.dialog.show()
        settings.load_settings()
        settings.load_tracked_processes()
        # Initialize variables
        self.isPressed = False
        self.current_notification = None
        # Setup UI components and connect signals
        self.setup_ui()
        # Start the process monitor thread
        self.process_monitor = ProcessMonitor(self)
        self.process_monitor.process_changed.connect(self.on_process_change)
        monitor_thread = threading.Thread(target=self.process_monitor.monitor_process, daemon=True)
        monitor_thread.start()

    def setup_ui(self):
        # Initialize UI elements
        self.profiles_list = self.dialog.profileList
        self.profiles_list_widget = QtWidgets.QWidget()
        self.profiles_list_content = QtWidgets.QVBoxLayout()
        self.profiles_list_widget.setLayout(self.profiles_list_content)
        self.profiles_list.setWidget(self.profiles_list_widget)
        
        # Define process_changer before using it
        self.process_changer = self.dialog.processSelectButton
        
        # Define default_checkbox before using it
        self.default_checkbox = self.dialog.defaultProfileCheck
        self.default_checkbox.clicked.connect(self.on_checkbox_change)
        
        # Key mappings
        self.key_to_button = {
            ('f13', 'key'): self.dialog.button1,
            ('f14', 'key'): self.dialog.button2,
            ('f15', 'key'): self.dialog.button3,
            ('f16', 'key'): self.dialog.button4,
            ('f17', 'key'): self.dialog.button5,
            ('f18', 'key'): self.dialog.button6,
            ('f19', 'key'): self.dialog.button7,
            ('f20', 'key'): self.dialog.button8,
            ('f21', 'key'): self.dialog.button9,
            ('f22', 'key'): self.dialog.button10,
            ('f23', 'key'): self.dialog.button11,
            ('f24', 'key'): self.dialog.button12,
            ('alt+shift+1', 'shortcut'): self.dialog.knob1,
            ('alt+shift+2', 'shortcut'): self.dialog.knob2,
            ('alt+shift+3', 'shortcut'): self.dialog.knob3,
            ('alt+shift+4', 'shortcut'): self.dialog.knob4,
            ('alt+shift+5', 'shortcut'): self.dialog.knob5,
            ('alt+shift+6', 'shortcut'): self.dialog.knob6
        }
        self.button_to_key = {
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
        # Connect signals and slots
        self.dialog.actionExit.triggered.connect(self.quit)
        # Load the initial profile
        self.current_profile = self.load_profile(settings.last_selected_profile)
        self.reload_buttons()
        self.dialog.closeEvent = self.on_dialog_close
        # Setup system tray icon
        self.tray_icon = QtWidgets.QSystemTrayIcon(QtGui.QIcon("assets/icon.png"))
        self.tray_icon.setToolTip("BagOnKey")
        self.tray_menu = QtWidgets.QMenu(self.dialog)
        open_action = self.tray_menu.addAction("Open")
        exit_action = self.tray_menu.addAction("Exit")
        self.tray_icon.setContextMenu(self.tray_menu)
        open_action.triggered.connect(self.dialog.show)
        exit_action.triggered.connect(self.quit)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
        # Connect additional signals
        self.dialog.actionDelete.triggered.connect(lambda: self.delete_dialog(self.current_profile.profile_name))
        self.dialog.actionAdd_new_profile.triggered.connect(self.create_profile)
        self.dialog.actionRename.triggered.connect(lambda: self.rename_profile(self.current_profile.profile_name))
        self.dialog.clearSelection.clicked.connect(self.clearProcessName)
        self.dialog.processSelectButton.clicked.connect(lambda: self.showFileDialog(self.dialog))
        self.dialog.actionAbout_BagOnKey.triggered.connect(uiElements.show_about_dialog)
        self.dialog.actionUse_this_tool_with_your_keyboard.triggered.connect(uiElements.show_help_dialog)
        self.threeKeys = self.dialog.action3_keys_1_knob
        self.twelveKeys = self.dialog.action12_keys_2_knobs
        self.threeKeys.triggered.connect(lambda: self.change_layout("mini", True))
        self.twelveKeys.triggered.connect(lambda: self.change_layout("classic", True))
        self.change_layout(settings.selected_layout)
        self.scroll_area = self.dialog.ideasList
        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout()
        self.description_scroll_area = self.dialog.description
        self.description_widget = QtWidgets.QWidget()
        self.description_layout = QtWidgets.QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.scroll_area.setWidget(self.content_widget)
        self.description_widget.setLayout(self.description_layout)
        self.description_scroll_area.setWidget(self.description_widget)
        self.exit_menu_bar = self.dialog.actionExit
        self.exit_menu_bar.triggered.connect(self.quit)
        # Set up keyboard event handlers
        for key, type_ in self.key_to_button.keys():
            if type_ == 'key':
                keyboard.on_release_key(key, self.on_button_click, suppress=True)
            else:
                keyboard.add_hotkey(key, self.on_button_click, args=(key,), suppress=True)
        # Populate the shortcuts list
        self.populate_shortcuts()

    def populate_shortcuts(self):
        last_category = ""
        for i in shortcut.shortcuts:
            if i.category != last_category:
                last_category = i.category
                collapsible_widget = self.CollapsibleWidget(i.category)
                self.content_layout.addWidget(collapsible_widget)
            button = self.DragButton(i.name, i.function, i.description, self)
            button.clicked.connect(lambda _, desc=i.description: self.refresh_description(desc))
            collapsible_widget.add_button(button)

    def refresh_description(self, desc):
        # Safely remove all widgets from the layout using deleteLater
        for i in reversed(range(self.description_layout.count())):
            self.description_layout.itemAt(i).widget().deleteLater()
        self.description_layout.addWidget(QtWidgets.QLabel(desc))

    class DragButton(QtWidgets.QPushButton):
        def __init__(self, label, shortcut, description, app_instance, *args, **kwargs):
            super().__init__(label, *args, **kwargs)
            self.data = label
            self.shortcut = shortcut
            self.description = description
            self.app_instance = app_instance
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
                
                # Call refresh_description on the app instance
                self.app_instance.refresh_description(self.description)
                self.show()

    class CollapsibleWidget(QtWidgets.QWidget):
        def __init__(self, title, parent=None):
            super().__init__(parent)
            self.setLayout(QtWidgets.QVBoxLayout())
            self.toggle_button = QtWidgets.QPushButton(title)
            self.toggle_button.setCheckable(True)
            self.toggle_button.setChecked(True)
            self.toggle_button.clicked.connect(self.toggle)
            self.group_box = QtWidgets.QGroupBox()
            self.group_layout = QtWidgets.QVBoxLayout()
            self.group_box.setLayout(self.group_layout)
            self.layout().addWidget(self.toggle_button)
            self.layout().addWidget(self.group_box)

        def add_button(self, button):
            self.group_layout.addWidget(button)

        def toggle(self, checked):
            self.group_box.setVisible(checked)

    def save_profile(self):
        profiles.save_profile(self.current_profile, f'profiles/{self.current_profile.profile_name}.json')

    def change_layout(self, setting, save=False):
        if setting == "":
            setting = "classic"
        if setting == "mini":
            self.dialog.button4.hide()
            self.dialog.button5.hide()
            self.dialog.button6.hide()
            self.dialog.button7.hide()
            self.dialog.button8.hide()
            self.dialog.button9.hide()
            self.dialog.button10.hide()
            self.dialog.button11.hide()
            self.dialog.button12.hide()
            self.dialog.dial2.hide()
            self.dialog.knob4.hide()
            self.dialog.knob5.hide()
            self.dialog.knob6.hide()
            self.threeKeys.setChecked(True)
            self.twelveKeys.setChecked(False)
        elif setting == "classic":
            self.dialog.button4.show()
            self.dialog.button5.show()
            self.dialog.button6.show()
            self.dialog.button7.show()
            self.dialog.button8.show()
            self.dialog.button9.show()
            self.dialog.button10.show()
            self.dialog.button11.show()
            self.dialog.button12.show()
            self.dialog.dial2.show()
            self.dialog.knob4.show()
            self.dialog.knob5.show()
            self.dialog.knob6.show()
            self.threeKeys.setChecked(False)
            self.twelveKeys.setChecked(True)
        if save:
            settings.selected_layout = setting
            settings.save_settings()
    
    def process_label_change(self, process_name):
        self.process_changer.setText(process_name + "\n(Click to change)")

    def load_profile(self, profile_name):
        name = profile_name
        profile = profiles.load_profile(f'profiles/{name}.json')
        if profile is None:
            profile = profiles.load_profile("profiles/default.json")
            name = "default"
        if name != settings.last_selected_profile:
            settings.last_selected_profile = name
            settings.save_settings()
            self.show_profile_notification(name)
        # Set the text for each button
        for i, button in enumerate(self.key_to_button.values()):
            if profile.layout[i].name == "":
                button.setText("None")
            else:
                button.setText(profile.layout[i].name)
        # Update profile list styles
        for i in range(self.profiles_list_content.count()):
            if self.profiles_list_content.itemAt(i).widget().text() == name:
                self.profiles_list_content.itemAt(i).widget().setStyleSheet("border-radius: 17px; border: 2px solid green; padding: 5px;")
            else:
                self.profiles_list_content.itemAt(i).widget().setStyleSheet("border-radius: 17px; border: 2px solid black; padding: 5px;")
        # Update process label
        for profile_name, tracked_process in settings.tracked_processes:
            if profile_name == name:
                self.process_label_change(tracked_process)
                break
        self.default_checkbox.setChecked(name == settings.default_profile)
        return profile

    def reload_buttons(self):
        # Clean the layout
        for i in reversed(range(self.profiles_list_content.count())):
            self.profiles_list_content.itemAt(i).widget().deleteLater()
        for profile in os.listdir("profiles"):
            profile_button = QtWidgets.QPushButton(profile.split(".")[0])
            if profile.split(".")[0] == self.current_profile.profile_name:
                profile_button.setStyleSheet("border-radius: 17px; border: 3px solid green; padding: 5px;")
            else:
                profile_button.setStyleSheet("border-radius: 17px; border: 2px solid black; padding: 5px;")
            def on_profile_click(profile_name):
                self.current_profile = self.load_profile(profile_name)
            profile_button.clicked.connect(lambda _, pn=profile.split(".")[0]: on_profile_click(pn))
            self.profiles_list_content.addWidget(profile_button)

    def on_checkbox_change(self):
        if self.default_checkbox.isChecked():
            settings.default_profile = self.current_profile.profile_name
            settings.save_settings()
        else:
            settings.default_profile = ""
            settings.save_settings()

    def on_dialog_close(self, event):
        self.dialog.hide()
        event.ignore()

    def on_tray_icon_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.dialog.show()

    def delete_dialog(self, profile_name):
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
            profiles.delete_profile(f'profiles/{profile_name}.json')
            self.current_profile = self.load_profile("default")
            settings.tracked_processes = [x for x in settings.tracked_processes if x[0] != profile_name]
            settings.save_tracked_processes()
            self.reload_buttons()
            delete_dialog.accept()
        
        def on_no_clicked():
            delete_dialog.reject()
        
        yes_button.clicked.connect(on_yes_clicked)
        #if the enter key is pressed, the yes button is clicked
        yes_button.setAutoDefault(True)
        no_button.clicked.connect(on_no_clicked)
        
        delete_dialog.exec()

    def create_profile(self):
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
            profile_name = input_field.text()
            profiles.create_profile(f'profiles/{profile_name}.json', profile_name)
            self.current_profile = self.load_profile(profile_name)
            settings.tracked_processes.append([profile_name, "None"])
            settings.save_tracked_processes()
            self.reload_buttons()
            create_dialog.accept()
        
        create_button.clicked.connect(on_create_clicked)
        create_button.setAutoDefault(True)
        cancel_button.clicked.connect(create_dialog.reject)
        
        create_dialog.exec()

    def rename_profile(self, profile_name):
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
            new_profile_name = input_field.text()
            #get the tracked process before it gets deleted from the renaming
            tracked_process = [x[1] for x in settings.tracked_processes if x[0] == profile_name][0]
            profiles.rename_profile(new_profile_name, self.current_profile, f'profiles/{profile_name}.json', f'profiles/{new_profile_name}.json')
            self.current_profile = self.load_profile(new_profile_name)
            # get the process name of the profile
            settings.tracked_processes = [x for x in settings.tracked_processes if x[0] != profile_name]
            settings.tracked_processes.append([new_profile_name, tracked_process])
            settings.save_tracked_processes()
            self.reload_buttons()
            rename_dialog.accept()
        
        rename_button.clicked.connect(on_rename_clicked)
        rename_button.setAutoDefault(True)
        cancel_button.clicked.connect(rename_dialog.reject)
        
        rename_dialog.exec()

    def clearProcessName(self):
        self.process_label_change("None")
        settings.tracked_processes = [x for x in settings.tracked_processes if x[0] != self.current_profile.profile_name]
        settings.tracked_processes.append([self.current_profile.profile_name, "None"])
        settings.save_tracked_processes()

    def showFileDialog(self, dialog):
        if self.current_profile.profile_name == "default":
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
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(dialog, "Open File", "", file_filter, options=options)
        if file_name:
            process_name = self.extractProcessName(file_name)
            # this process name will be the one to be used for tracking the process when the foreground process changes
            settings.tracked_processes = [x for x in settings.tracked_processes if x[0] != self.current_profile.profile_name]
            settings.tracked_processes.append([self.current_profile.profile_name, process_name])
            self.process_label_change(process_name)
            settings.save_tracked_processes()

    def extractProcessName(self, file_path):
        return os.path.basename(file_path)

    def on_button_click(self, event):
        isShortcut = False
        button_list = list(self.button_to_key.values())
        if isinstance(event, str):
            isShortcut = True
        process_name = self.get_foreground_process_name()
        if not isShortcut:
            logging.info(f'Key {event.name.upper()} pressed in process {process_name}')
            command = self.current_profile.layout[button_list.index(event.name)].command
        else:
            logging.info(f'Shortcut {event} pressed in process {process_name}')
            command = self.current_profile.layout[button_list.index(event)].command
        
        if (command != ""):
            if (command.startswith("BagOnKey")):
                if (command.split("|")[1] == "openLink"):
                    specialFunctions.openLink(command.split("|")[2])
            else:
                keyboard.press_and_release(command)

    def get_foreground_process_name(self):
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process = psutil.Process(pid)
            return process.name()
        except psutil.Error:
            return "Unknown"
        except ValueError:
            return "Unknown"

    def show_profile_notification(self, profile_name):
        if self.current_notification:
            self.current_notification.close()
        self.current_notification = PopupNotification(profile_name)
        self.current_notification.show_notification()

    def clear_current_notification(self):
        self.current_notification = None

    def on_process_change(self, process_name):
        found = False
        for profile_name, tracked_process in settings.tracked_processes:
            if tracked_process == process_name:
                self.current_profile = self.load_profile(profile_name)
                found = True
                break
        if not found and settings.default_profile != "":
            self.current_profile = self.load_profile(settings.default_profile)

class CustomUiLoader(QUiLoader):
    def createWidget(self, className, parent=None, name=''):
        if (className == 'DropLabel'):
            widget = DropLabel(parent)
            widget.setObjectName(name)
            return widget
        return super().createWidget(className, parent, name)

class PopupNotification(QtWidgets.QWidget):
    def __init__(self, profile_name, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | 
            QtCore.Qt.FramelessWindowHint | 
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # Ensure the background is transparent

        global dial_position

        # Create a frame to hold the layout and apply the squircle effect
        self.frame = QtWidgets.QFrame(self)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 255);
                border-radius: 15px;
            }
            QLabel {
                color: white;
                font-size: 16px;
            }
        """)

        layout = QtWidgets.QHBoxLayout(self.frame)

        # Add icon to the popup
        icon_label = QtWidgets.QLabel()
        icon = QtGui.QIcon("assets/icon.png")  # Replace with the path to your icon
        icon_pixmap = icon.pixmap(32, 32)  # Adjust the size as needed
        icon_label.setPixmap(icon_pixmap)
        layout.addWidget(icon_label)

        label = QtWidgets.QLabel(f"Profile: {profile_name}")
        layout.addWidget(label)

        self.frame.adjustSize()
        self.adjustSize()
        self.move_to_corner()

        # Add opacity effect
        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # Create fade-in animation
        self.fade_in_animation = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(500)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)

        # Create fade-out animation
        self.fade_out_animation = QtCore.QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(500)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.finished.connect(self.hide_notification)

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
        self.fade_in_animation.start()
        QtCore.QTimer.singleShot(duration, self.start_fade_out)

    def start_fade_out(self):
        self.fade_out_animation.start()

    def hide_notification(self):
        self.close()

class ProcessMonitor(QObject):
    process_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.last_process = None

    def monitor_process(self):
        while True:
            process_name = self.parent.get_foreground_process_name()
            if process_name != self.last_process:
                logging.info(f'Foreground process changed to {process_name}')
                self.last_process = process_name
                self.process_changed.emit(process_name)
            time.sleep(0.5)

if __name__ == "__main__":
    app = BagOnKeyApp(sys.argv)
    sys.exit(app.exec())