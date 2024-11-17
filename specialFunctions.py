import webbrowser
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout

def openLink(link):
    webbrowser.open(link)
    return

def getNameAndLink():
    QApplication.instance()

    dialog = QDialog()
    dialog.setWindowTitle('Enter Name and Link')

    nameLabel = QLabel('Name:')
    nameEdit = QLineEdit()

    linkLabel = QLabel('Link:')
    linkEdit = QLineEdit()

    buttonOk = QPushButton('OK')
    buttonCancel = QPushButton('Cancel')

    buttonLayout = QHBoxLayout()
    buttonLayout.addWidget(buttonOk)
    buttonLayout.addWidget(buttonCancel)

    layout = QVBoxLayout()
    layout.addWidget(nameLabel)
    layout.addWidget(nameEdit)
    layout.addWidget(linkLabel)
    layout.addWidget(linkEdit)
    layout.addLayout(buttonLayout)
    dialog.setLayout(layout)

    buttonOk.clicked.connect(dialog.accept)
    buttonCancel.clicked.connect(dialog.reject)

    if dialog.exec() == QDialog.Accepted:
        name = nameEdit.text()
        link = f"BagOnKey|openLink|{linkEdit.text()}"
        return name, link
    else:
        return None, None

def getCustomShortcut():
    QApplication.instance()

    dialog = QDialog()
    dialog.setWindowTitle('Enter Name and Shortcut')

    nameLabel = QLabel('Name:')
    nameLabel.setOpenExternalLinks(True)
   
    nameEdit = QLineEdit()

    linkLabel = QLabel('Shortcut: (Hover here for more info)')
    linkLabel.setToolTip('Examples may include (don\'t include the hypen in the command):\n- ctrl+shift+1\n- f1\n- alt+f4, enter\n- alt+3\n\nThis tool uses boppreh\'s "keyboard" project. For more information, check keyboard\'s documentation.')
    linkEdit = QLineEdit()

    buttonOk = QPushButton('OK')
    buttonCancel = QPushButton('Cancel')

    buttonLayout = QHBoxLayout()
    buttonLayout.addWidget(buttonOk)
    buttonLayout.addWidget(buttonCancel)

    layout = QVBoxLayout()
    layout.addWidget(nameLabel)
    layout.addWidget(nameEdit)
    layout.addWidget(linkLabel)
    layout.addWidget(linkEdit)
    layout.addLayout(buttonLayout)
    dialog.setLayout(layout)

    buttonOk.clicked.connect(dialog.accept)
    buttonCancel.clicked.connect(dialog.reject)

    if dialog.exec() == QDialog.Accepted:
        name = nameEdit.text()
        link = linkEdit.text()
        return name, link
    else:
        return None, None
