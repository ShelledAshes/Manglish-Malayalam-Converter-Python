from PyQt5.QtWidgets import (QMainWindow, QApplication, QComboBox, QPlainTextEdit,
                             QTableWidget, QTableWidgetItem, QWidget, QHBoxLayout, QLineEdit)
from PyQt5.QtCore import Qt, QEvent
from PyQt5 import uic
import sys


class IPlainTextEdit(QPlainTextEdit):
    def __init__(self):
        super(IPlainTextEdit, self).__init__()

    def keyPressEvent(self, event):
        # if event.key() == Qt.Key_Space:
        #     print("space pressed.....")
            # return
        super(QPlainTextEdit, self).keyPressEvent(event)

class OnTimeWindow(QWidget):
    def __init__(self):
        super().__init__()

        # uic.loadUi("UiFiles/converterontime.ui", self)
        self.setWindowTitle('Convert on time')

        # self.txtMalConverter = self.findChild(QPlainTextEdit, "txtMalConverter")
        # self.cboMoreOptions = self.findChild(QComboBox, "cboMoreOptions")

        self.txtMalConverter = IPlainTextEdit()
        self.cboMoreOptions = QComboBox()

        layout = QHBoxLayout()
        layout.addWidget(self.txtMalConverter)
        layout.addWidget(self.cboMoreOptions)
        self.setLayout(layout)

        self.txtMalConverter.textChanged.connect(self.word_entered)

        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            print(")))))), space pressed....")

        super(QWidget, self).__init__()


    def word_entered(self):

        text = self.txtMalConverter.toPlainText()
        cursor = self.txtMalConverter.textCursor()
        pos = cursor.position()

        word_list = text[:pos].split()
        print("....", word_list[-1])


if __name__ == "__main__":

    app = QApplication(sys.argv)
    UIWindow = OnTimeWindow()
    # sys.excepthook = UIWindow.excepthook
    app.exec()