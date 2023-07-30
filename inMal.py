from PyQt5.QtWidgets import (QMainWindow, QPushButton, QPlainTextEdit, QComboBox, QLineEdit, QCheckBox)
from PyQt5.QtCore import Qt, QEvent
from PyQt5 import uic

from pynput.keyboard import Listener, KeyCode
import re
import translate as T
import malConv as mc
from gen import LOG


class MalWindow(QMainWindow):

    def __init__(self, text, me_dict):
        super(MalWindow, self).__init__()
        uic.loadUi("UiFiles/inMalText.ui", self)

        self.setWindowTitle('In Mal')

        self.malEngDict = me_dict
        self.markedMal_word = ''
        self.ex = '\s|(\.)|(\,)|(\;)|(\:)|(\!)|(\?)|(\/)|(\()|(\-)|(\“)|(\”)'

        self.txtMal = self.findChild(QPlainTextEdit, "txtMal")
        self.txtMal.setPlainText(text)
        self.cmdMoreOptions = self.findChild(QPushButton,"cmdMoreOptions")
        self.cmdReplace = self.findChild(QPushButton,"cmdReplace")
        self.cboMalOptionList = self.findChild(QComboBox,"cboMalOptionList")
        self.cboExistingMalList = self.findChild(QComboBox, "cboExistingMalList")
        self.txtEnterMalWord = self.findChild(QLineEdit,"txtEnterMalWord")

        self.txtEnterMalWord.installEventFilter(self)
        self.txtMal.setReadOnly(True)
        self.txtMal.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.txtMal.setFocus()

        self.cboExistingMalList.setVisible(False)

        self.txtEngWord = self.findChild(QLineEdit, "txtEngWord")
        self.txtMalWord = self.findChild(QLineEdit, "txtMalWord")

        self.cmdIncrementFrequency = self.findChild(QPushButton,"cmdIncrementFrequency")
        self.chkAutoIncreFrequency = self.findChild(QCheckBox,"chkAutoIncreFrequency")

        self.chkAutoIncreFrequency.setChecked(True)
        self.resize(1000,450)

        self.txtMalCursor = self.txtMal.textCursor()
        self.txtmal_cursor_pos = 0

        self.cmdMoreOptions.clicked.connect(self.showOptions)
        self.cmdReplace.clicked.connect(self.replaceMalWord)
        self.txtMal.selectionChanged.connect(self.handleSelectionChanged)
        self.cmdIncrementFrequency.clicked.connect(self.autoIncrementFreq)

        listener = Listener(on_press=lambda event: self.on_press(event))
        listener.start()

    def on_press(self,key):
        self.keyK = key

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and source is self.txtEnterMalWord:
            if event.modifiers() & Qt.AltModifier:
                if event.key() == Qt.Key_S or self.keyK == KeyCode(char='s'):
                    print('alt and s pressed')
                    if self.txtEnterMalWord.hasFocus():
                        self.txtMal.setFocus()
                        cur = self.txtMal.textCursor()
                        cur.setPosition(self.txtmal_cursor_pos)
                        self.txtMal.setTextCursor(cur)
        return super(MalWindow, self).eventFilter(source, event)

    def keyPressEvent(self, event):

        if event.modifiers() & Qt.AltModifier:

            if event.key() == Qt.Key_W or self.keyK == KeyCode(char='w'):
                self.txtEnterMalWord.setText(self.markedMal_word)

            if event.key() == Qt.Key_E or self.keyK == KeyCode(char='e'):
                opt_text = self.cboMalOptionList.currentText()
                if opt_text != '': self.txtEnterMalWord.setText(opt_text)

            if event.key() == Qt.Key_S or self.keyK == KeyCode(char='s'):
                if self.txtMal.hasFocus():
                    self.txtmal_cursor_pos = self.txtMal.textCursor().position()
                    self.txtEnterMalWord.setFocus()

    def closeEvent(self, event):
        if self.chkAutoIncreFrequency.isChecked():
            self.autoIncrementFreq()

    def autoIncrementFreq(self):

        self.chkAutoIncreFrequency.setChecked(False)
        mal_text = self.txtMal.toPlainText()
        word_list = [word for word in re.split(self.ex, mal_text) if word]
        T.incrementFrequency(self.malEngDict, word_list)

    def handleSelectionChanged(self):

        cursor = self.txtMal.textCursor()
        marked_mal_word = re.sub(self.ex, "", cursor.selectedText())

        if marked_mal_word != '' : #use split here
            self.markedMal_word = marked_mal_word
            self.txtMalWord.setText(self.markedMal_word)
            self.txtEngWord.setText(self.malEngDict.get(self.markedMal_word,'****'))

            eng_word = self.txtEngWord.text()
            existing_word_list = T.checkSavedWords(eng_word)
            if len(existing_word_list) > 1:
                self.cboExistingMalList.clear()
                self.cboExistingMalList.setVisible(True)
                for word in existing_word_list:
                    if word[0] != '':
                        self.cboExistingMalList.addItem(word[0])
            else:
                self.cboExistingMalList.setVisible(False)

    def replaceMalWord(self):

        rmal_word = self.txtEnterMalWord.text()

        if rmal_word == '':
            if self.cboExistingMalList.isVisible():
                rmal_word = self.cboExistingMalList.currentText()
            else:
                rmal_word = self.cboMalOptionList.currentText()

        if rmal_word != '':

            if self.markedMal_word in self.malEngDict:
                self.malEngDict[rmal_word] = self.malEngDict.pop(self.markedMal_word)#replacing mal key in dict

            mal_text = self.txtMal.toPlainText()
            self.txtMal.setPlainText('')
            converted_text = T.getReplacedMalText(mal_text, self.markedMal_word, rmal_word, self.malEngDict[rmal_word], self.ex)
            self.txtMal.setPlainText(converted_text)
            self.txtMalWord.setText(rmal_word)
            T.decrement_replace(self.markedMal_word, rmal_word, self.malEngDict[rmal_word])
        else:
            print('no word for replacement')

    def showOptions(self):

        self.txtEnterMalWord.setText('')
        cursor = self.txtMal.textCursor()
        cursor_text = cursor.selectedText()

        if cursor_text != '':
            self.markedMal_word = re.sub(self.ex, "", cursor_text)
            marked_eng_word = self.malEngDict.get(self.markedMal_word, '')

            if marked_eng_word == '':
                marked_eng_word = T.getEngWordFromDB(self.markedMal_word)

            if self.markedMal_word != '':
                mal_word_list = mc.more_mal_options(marked_eng_word)
                self.cboMalOptionList.clear()
                for i in mal_word_list:
                    self.cboMalOptionList.addItem(i)

