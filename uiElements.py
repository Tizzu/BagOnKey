from PySide6 import QtGui, QtWidgets
from PySide6 import QtCore

def show_about_dialog():
    about_dialog = QtWidgets.QDialog()
    about_dialog.setWindowTitle("About")
    about_dialog.setWindowIcon(QtGui.QIcon("assets/icon.png"))
    about_dialog.resize(200, 100)
    layout = QtWidgets.QVBoxLayout()
    about_dialog.setLayout(layout)
    # Add the app icon to the dialog content
    icon_label = QtWidgets.QLabel()
    icon_pixmap = QtGui.QPixmap("assets/icon.png")
    icon_label.setPixmap(icon_pixmap)
    layout.addWidget(icon_label, alignment=QtCore.Qt.AlignCenter)
    #center the text and button
    layout.setAlignment(QtCore.Qt.AlignCenter)
    # Fix the clickable link in the label
    label_text = """
    BagOnKey is a tool to create custom shortcuts for your keyboard<br><br>
    Made with &lt;3 by Valentino Artizzu<br>
    <a href='https://tizzu.github.io'>My website</a><br><br>Made with Python and Qt
    """
    label = QtWidgets.QLabel(label_text)
    label.setOpenExternalLinks(True)
    label.setStyleSheet("""
    QLabel {
        text-align: center;
    }
""")
    layout.addWidget(label)
    layout.setAlignment(QtCore.Qt.AlignCenter)
    ok_button = QtWidgets.QPushButton("Got it!")
    layout.addWidget(ok_button)
    ok_button.clicked.connect(about_dialog.accept)
    about_dialog.exec()

def show_help_dialog():
    help_dialog = QtWidgets.QDialog()
    help_dialog.setWindowTitle("Help")
    help_dialog.setWindowIcon(QtGui.QIcon("assets/icon.png"))
    help_dialog.resize(200, 100)
    layout = QtWidgets.QVBoxLayout()
    help_dialog.setLayout(layout)
    #center the text and button
    layout.setAlignment(QtCore.Qt.AlignCenter)
    # Fix the clickable link in the label
    label_text = """ This is a quick guide on how to use BagOnKey:<br><br>
    First of all, you should reconfigure the buttons of your keyboard to make them work with this program.<br>
    Use your keyboard tool to remap all the buttons you want to use with BagOnKey to the F13-F24 keys.<br>
    Use the same tool to remap the knobs to alt+shift+1 ... alt+shift+3 for the first knob, alt+shift+4 ... alt+shift+6 for the second knob.<br>
    This tool supports up to 12 buttons and 2 knobs.<br>
    In this version you can set the 3 buttons + 1 knob layout or the 12 buttons + 2 knobs one. If you have more than 3 buttons and less than 12,<br> you can use the 12 buttons layout and leave the unused buttons empty. The same goes for the knobs.<br>    
    """
    label = QtWidgets.QLabel(label_text)
    label.setOpenExternalLinks(True)
    label.setStyleSheet("""
    QLabel {
        text-align: center;
    }
""")
    layout.addWidget(label)
    ok_button = QtWidgets.QPushButton("Got it!")
    layout.addWidget(ok_button)
    ok_button.clicked.connect(help_dialog.accept)
    help_dialog.exec()