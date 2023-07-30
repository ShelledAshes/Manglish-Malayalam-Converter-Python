
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QPlainTextEdit, QCheckBox,
                             QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QLineEdit)
from PyQt5 import uic
from PyQt5.QtCore import Qt

import sys
import translate as T
import malConv as mc
from gen import DB as db, LOG


class Popup(QWidget):

    def __init__(self, wdgt):
        super().__init__()

        self.widget = wdgt
        self.widget.setVisible(True)

        layout = QVBoxLayout()
        layout.addWidget(self.widget)
        self.setLayout(layout)

        self.show()


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        uic.loadUi("UiFiles/converter.ui", self)
        self.setWindowTitle('Eng Converter')

        """PushButton"""
        self.cmdConverter = self.findChild(QPushButton, "cmdConvert")
        self.cmdViewData = self.findChild(QPushButton, "cmdViewData")
        self.cmdConvertOnTime = self.findChild(QPushButton, "cmdConvertOnTime")

        self.cmdEdit = self.findChild(QPushButton, "cmdEdit")
        self.cmdSave = self.findChild(QPushButton, "cmdSave")
        self.cmdDelete = self.findChild(QPushButton, "cmdDelete")
        self.cmdInsert = self.findChild(QPushButton, "cmdInsert")
        self.cmdUndo = self.findChild(QPushButton, "cmdUndo")

        """TextLineEdit"""
        self.txtEngText = self.findChild(QPlainTextEdit, "txtEngText")

        """LineEdit"""
        self.txtSearchHere = self.findChild(QLineEdit, "txtSearchHere")

        """Checkbox"""
        self.chkFreqIncrement = self.findChild(QCheckBox, "chkFreqIncrement")
        self.chkInitialInsert = self.findChild(QCheckBox, "chkInitialInsert")

        """Table"""
        self.tableView = self.findChild(QTableWidget, "tableView")

        """Widget"""
        self.wDatatable = self.findChild(QWidget, "wDatatable")

        """Variables"""
        self.nonchars = '\.\,\!\?\;\“\”\"' + "\'"
        self.w, self.p = False, False
        self.engEditList, self.malEditList = [], []
        self.delWordList, self.wordInsertList, self.tempInsertList = [], [], []
        self.eng_col, self.mal_col, self.freq_col = 0, 1, 2
        self.searchText = ''

        f = self.txtEngText.font()
        f.setPointSize(11)
        self.txtEngText.setFont(f)

        """Setting Properties"""
        self.wDatatable.setVisible(False)
        self.chkInitialInsert.setChecked(True)

        self.cmdUndo.setEnabled(False)
        self.cmdSave.setEnabled(False)
        self.cmdDelete.setEnabled(False)
        self.cmdInsert.setEnabled(False)

        """button clicked functions"""
        self.cmdConverter.clicked.connect(self.convertToMal)
        self.cmdViewData.clicked.connect(self.openTableView)
        self.cmdEdit.clicked.connect(self.editClicked)
        self.cmdDelete.clicked.connect(self.deleteRow)
        self.cmdSave.clicked.connect(self.saveTableData)
        self.cmdInsert.clicked.connect(self.tableInsert)
        self.cmdUndo.clicked.connect(self.undoClicked)
        self.tableView.cellChanged.connect(self.tblViewEdited)
        self.txtSearchHere.textChanged.connect(self.searchTextChanged)
        self.cmdConvertOnTime.clicked.connect(self.on_time_convertion)

        self.show()


    def on_time_convertion(self):
        from malConvOnTime import OnTimeWindow

        self.closeChildWindows()
        self.o = OnTimeWindow()
        self.o.show()


    def searchTextChanged(self, text):
        self.searchText = text
        self.setTableData(self.searchText)

    def enablingButtons(self, yes):

        self.txtSearchHere.setEnabled(not yes)
        self.cmdEdit.setEnabled(not yes)
        self.cmdUndo.setEnabled(yes)
        self.cmdSave.setEnabled(yes)
        self.cmdDelete.setEnabled(yes)
        self.cmdInsert.setEnabled(yes)

    def undoClicked(self):
        self.enablingButtons(False)
        self.clear_table_lists()
        self.setTableData(self.searchText)

    def tableInsert(self):

        insert_row = self.tableView.currentRow()+1
        self.tableView.insertRow(insert_row)
        self.tempInsertList.append(insert_row)

    def checkforInsertedWords(self):

        if len(self.tempInsertList) > 0:
            for row in self.tempInsertList:
                eItem = self.tableView.item(row, self.eng_col)
                mItem = self.tableView.item(row, self.mal_col)
                if eItem != None and eItem != None:
                    eWord, mWord = eItem.text(), mItem.text()
                    if eWord != '' and mWord != '':
                        self.wordInsertList.append((eWord, mWord))

    def saveTableData(self):

        self.checkforInsertedWords()
        cleared_lists = T.alterDataInDb(self.engEditList, self.malEditList, self.delWordList, self.wordInsertList)
        self.engEditList, self.malEditList = cleared_lists[0], cleared_lists[1]
        self.delWordList, self.wordInsertList = cleared_lists[2], cleared_lists[3]
        self.setTableData(self.searchText)

        self.enablingButtons(False)
        self.clear_table_lists()

    def clear_table_lists(self):
        self.engEditList, self.malEditList = [], []
        self.delWordList, self.wordInsertList, self.tempInsertList = [], [], []

    def tblViewEdited(self):

        row, col = self.tableView.currentRow(), self.tableView.currentColumn()
        eId = self.tableView.model().index(row, 0).data(1001)
        mId = self.tableView.model().index(row, 1).data(1001)

        if col == self.eng_col:
            edited_word = self.tableView.item(row, col).text()
            self.engEditList.append((eId, mId, edited_word))
        elif col == self.mal_col or col == self.freq_col:
            edited_word = self.tableView.item(row, self.mal_col).text()
            freq = self.tableView.item(row, self.freq_col).text()
            self.malEditList.append((mId, edited_word, freq))

    def editClicked(self):
        self.setTableReadOnly(False)
        self.enablingButtons(True)

    def deleteRow(self):

        row, col = self.tableView.currentRow(), self.tableView.currentColumn()
        eId = self.tableView.model().index(row, 0).data(1001)
        mId = self.tableView.model().index(row, 1).data(1001)

        self.delWordList.append((eId, mId))
        self.tableView.removeRow(row)

        if row in self.tempInsertList:
            self.tempInsertList.remove(row)

    def setTableData(self, search_word=''):

        self.tableView.blockSignals(True)
        self.tableView.clear()

        query = "select w.id as eid, wl.wordid as mid,w.pattern, wl.word, wl.frequency\
                    from words as w\
                    left join wordlist as wl on wl.engword_id = w.id "
        if search_word != '':
            query += f"WHERE w.pattern like '%{search_word}%' or wl.word like '%{search_word}%' "
        query += "order by w.pattern"

        tbl_data = db.getFieldData(query)

        self.tableView.setRowCount(len(tbl_data))
        self.tableView.setColumnCount(3)
        self.tableView.setHorizontalHeaderLabels(["Eng word", "Mal word", "Times used"])

        for row, rowData in enumerate(tbl_data):
            eId, mId, eWord, mWord, freq = rowData

            self.tableView.setItem(row, 0, QTableWidgetItem(eWord))
            self.tableView.model().setData(self.tableView.model().index(row, 0), str(eId), 1001)
            self.tableView.setItem(row, 1, QTableWidgetItem(mWord))
            self.tableView.model().setData(self.tableView.model().index(row, 1), str(mId), 1001)
            self.tableView.setItem(row, self.freq_col, QTableWidgetItem(str(freq)))

        self.setTableReadOnly(True)
        self.tableView.blockSignals(False)

    def setTableReadOnly(self, read_only):
        self.tableView.blockSignals(True)

        editFlag = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        editFlag = editFlag | Qt.ItemIsEditable if not read_only else editFlag

        for row in range(self.tableView.rowCount()):
            for col in range(self.tableView.columnCount()):
                item = self.tableView.item(row, col)
                item.setFlags(editFlag)
                self.tableView.setItem(row, col, item)

        self.tableView.blockSignals(False)

    def openTableView(self):

        self.setTableData()
        self.p = Popup(self.wDatatable)
        self.setFocusProxy(self.p)
        self.p.resize(650, 450)
        self.p.show()

    def show_new_window(self, mal_text, me_dict):
        from inMal import MalWindow

        self.closeChildWindows()
        self.w = MalWindow(mal_text, me_dict)
        self.w.show()

    def convertToMal(self):

        exec_keys = 0
        exec_keys = exec_keys + 1 if self.chkFreqIncrement.isChecked() else exec_keys
        exec_keys = exec_keys + 2 if self.chkInitialInsert.isChecked() else exec_keys

        text_to_convert = self.txtEngText.toPlainText()
        mal_d, me_dict = mc.convertToMal(text_to_convert, exec_keys)
        self.show_new_window(mal_d, me_dict)

    def closeChildWindows(self):
        if self.w:
            if self.w.chkAutoIncreFrequency.isChecked():
                self.w.autoIncrementFreq()
            self.w.close()

        if self.p:
            self.p.close()

    def closeEvent(self, event):
        self.closeChildWindows()

    def excepthook(self, exc_type, exc_value, exc_tb):
        import traceback

        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print("error message:\n", tb)
        self.popUpWarning(tb)

    def popUpWarning(self, msg):
        import popupMsg as Pop

        self.a = Pop.WarningWindow(msg)
        self.a.show()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    UIWindow = UI()
    sys.excepthook = UIWindow.excepthook
    app.exec()
