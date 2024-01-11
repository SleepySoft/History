from datetime import datetime
from typing import Tuple

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QDateTimeEdit, QDialog, QDialogButtonBox
from PyQt5.QtCore import QDateTime


class DateTimePicker(QDialog):
    def __init__(self, parent=None):
        super(DateTimePicker, self).__init__(parent)

        self.dateTimeEdit = QDateTimeEdit(self)
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.dateTimeEdit.setCalendarPopup(True)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.dateTimeEdit)
        layout.addWidget(self.buttonBox)

        self.setWindowTitle('Date Time Picker')

    def dateTime(self):
        return self.dateTimeEdit.dateTime()

    @staticmethod
    def pickDateTime(parent=None) -> Tuple[datetime, bool]:
        dialog = DateTimePicker(parent)
        result = dialog.exec_()
        dt = dialog.dateTime()
        return dt.toPyDateTime(), result == QDialog.Accepted


# class MainWindow(QWidget):
#     def __init__(self):
#         super(MainWindow, self).__init__()
#
#         self.button = QPushButton('选择日期和时间', self)
#         self.button.clicked.connect(self.showDialog)
#
#         layout = QVBoxLayout(self)
#         layout.addWidget(self.button)
#
#     def showDialog(self):
#         date, time, ok = DateTimeDialog.getDateTime()
#         if ok:
#             print(f"选择的日期是 {date}, 时间是 {time}")


if __name__ == '__main__':
    app = QApplication([])
    date, time, ok = DateTimePicker.pickDateTime()
    if ok:
        print(f"选择的日期是 {date}, 时间是 {time}")
    app.exec_()
