
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QApplication, QPlainTextEdit)

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys


class WarningWindow(QWidget):

    def __init__(self, msg):
        super().__init__()

        self.setWindowTitle('Warning')

        self.lblMsg = QPlainTextEdit(msg)
        self.cmdOK = QPushButton('&OK')

        myFont = QFont()
        # myFont.setBold(True)
        myFont.setPointSize(10)

        self.lblMsg.setFont(myFont)
        layout = QVBoxLayout()
        layout.addWidget(self.lblMsg)
        layout.addWidget(self.cmdOK)
        self.setLayout(layout)
        self.resize(900, 300)

        self.lblMsg.setEnabled(False)
        self.cmdOK.clicked.connect(self.closePopup)

        self.show()

    def on_press(self,key):
        self.keyK = key


    def closePopup(self):
        # error_dialog = QErrorMessage()
        # self.error_dialog.showMessage('Oh no!')
        # self.cmdOK.setText(True)
        self.close()


if __name__ == '__main__':
    # sys.excepthook = gf.excepthook

    app = QApplication(sys.argv)
    UIWindow = WarningWindow('msh')
    app.exec()
    # sys.exit(app.exec_())





