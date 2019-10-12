import sys
import traceback
from functools import partial
from collections import OrderedDict

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QStyledItemDelegate, QTreeWidgetItem, QComboBox, QInputDialog, QFileDialog

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QHBoxLayout, QTableWidgetItem, \
    QWidget, QPushButton, QDockWidget, QLineEdit, QAction, qApp, QMessageBox, QDialog, QVBoxLayout, QLabel, QTextEdit, \
    QListWidget, QShortcut

from core import *
from Utility.ui_utility import *


# ---------------------------------------------------- FilterEditor ----------------------------------------------------

class FilterEditor(QWidget):
    def __init__(self, parent: QWidget = None):
        super(FilterEditor, self).__init__(parent)

        self.__sources = []
        self.__includes = []
        self.__excludes = []

        self.__combo_focus = QComboBox()
        self.__source_list = EasyQListSuite()
        self.__include_list = EasyQListSuite()
        self.__exclude_list = EasyQListSuite()

        self.__init_ui()
        self.__config_ui()

    def get_filter(self):
        pass

    def set_filter(self):
        pass

    # --------------------------------------------- Private ---------------------------------------------

    def __init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        group, layout = create_v_group_box('Source Selector')
        layout.addWidget(self.__source_list)
        main_layout.addWidget(group)

        group_in, layout_in = create_v_group_box('Include Label Tags')
        group_ex, layout_ex = create_v_group_box('Exclude Label Tags')
        layout_in.addWidget(self.__include_list)
        layout_ex.addWidget(self.__exclude_list)
        main_layout.addLayout(horizon_layout([group_in, group_ex]))

        group, layout = create_v_group_box('Focus Label')
        layout.addWidget(self.__combo_focus)
        main_layout.addWidget(group)

    def __config_ui(self):
        self.__source_list.set_add_handler(self.__on_source_add)
        self.__source_list.set_remove_handler(self.__on_source_remove)

        self.__include_list.set_add_handler(self.__on_include_add)
        self.__include_list.set_remove_handler(self.__on_include_remove)

        self.__exclude_list.set_add_handler(self.__on_exclude_add)
        self.__exclude_list.set_remove_handler(self.__on_exclude_remove)

    def __on_source_add(self):
        fname, ftype = QFileDialog.getOpenFileNames(self,
                                                    'Select History Files',
                                                    HistoricalRecordLoader.get_local_depot_root(),
                                                    'History Files (*.his)')
        self.__sources.extend(fname)
        self.__sources = list(set(self.__sources))

        self.__source_list.update_item()

    def __on_source_remove(self):
        pass

    def __on_include_add(self):
        pass

    def __on_include_remove(self):
        pass

    def __on_exclude_add(self):
        pass

    def __on_exclude_remove(self):
        pass


# ----------------------------------------------------- HistoryUi ------------------------------------------------------

class HistoryUi(QMainWindow):
    def __init__(self):
        super(HistoryUi, self).__init__()
        self.init_ui()
        self.init_menu()

    def init_ui(self):
        self.statusBar().showMessage('Ready')

        self.resize(1280, 800)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center());
        self.setWindowTitle('History - Sleepy')

    def init_menu(self):
        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu('File')
        menu_file = menu_bar.addMenu('Config')
        menu_help = menu_bar.addMenu('Help')

        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit app')
        exit_action.triggered.connect(qApp.quit)
        menu_file.addAction(exit_action)

        config_action = QAction('&C', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit app')
        exit_action.triggered.connect(qApp.quit)
        menu_file.addAction(exit_action)

        help_action = QAction('&Help', self)
        help_action.setShortcut('Ctrl+H')
        help_action.setStatusTip('Open help Window')
        help_action.triggered.connect(self.on_menu_help)
        menu_help.addAction(help_action)

        about_action = QAction('&About', self)
        about_action.setShortcut('Ctrl+B')
        about_action.setStatusTip('Open about Window')
        about_action.triggered.connect(self.on_menu_about)
        menu_help.addAction(about_action)


# ------------------------------------------------ File Entry : main() -------------------------------------------------

def main():
    app = QApplication(sys.argv)
    wnd = FilterEditor()
    wnd.showNormal()
    app.exec_()


# ----------------------------------------------------------------------------------------------------------------------

def exception_hook(type, value, tback):
    # log the exception here
    print('Exception hook triggered.')
    print(type)
    print(value)
    print(tback)
    # then call the default handler
    sys.__excepthook__(type, value, tback)


if __name__ == "__main__":
    sys.excepthook = exception_hook
    try:
        main()
    except Exception as e:
        print('Error =>', e)
        print('Error =>', traceback.format_exc())
        exit()
    finally:
        pass






