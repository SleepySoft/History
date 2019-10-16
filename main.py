import sys
import traceback
from PyQt5.QtWidgets import QApplication, QScrollBar, QSlider

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QStyledItemDelegate, QTreeWidgetItem, QComboBox, QInputDialog, QFileDialog

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QHBoxLayout, QTableWidgetItem, \
    QWidget, QPushButton, QDockWidget, QLineEdit, QAction, qApp, QMessageBox, QDialog, QVBoxLayout, QLabel, QTextEdit, \
    QListWidget, QShortcut

from core import *
from editor import *
from viewer import *
from filter import *
from indexer import *
from Utility.ui_utility import *


# --------------------------------------------------- Thread Editor ----------------------------------------------------

class AppearanceEditor(QWidget):
    def __init__(self, parent: QWidget = None):
        super(AppearanceEditor, self).__init__(parent)

        self.__radio_horizon = QRadioButton('Horizon')
        self.__radio_vertical = QRadioButton('Vertical')

        self.__label_position = QLabel('50')
        self.__slider_position = QSlider(Qt.Horizontal)
        self.__slider_position.setMinimum(0)
        self.__slider_position.setMaximum(100)
        self.__slider_position.setSliderPosition(50)

        self.__group_thread_editor = None
        self.__layout_thread_editor = None
        self.__button_thread_add = QPushButton('Add')
        self.__label_thread_place_holder = QHBoxLayout()

        self.__init_ui()

    def __init_ui(self):
        self.__label_thread_place_holder.addWidget(QLabel(''), 100)
        self.__label_thread_place_holder.addWidget(self.__button_thread_add, 0)

        group_appearance, layout_appearance = create_v_group_box('Appearance')
        layout_appearance.addLayout(horizon_layout([QLabel('Layout  '), self.__radio_horizon, self.__radio_vertical]))
        layout_appearance.addLayout(horizon_layout([QLabel('Position'), self.__slider_position, self.__label_position]))

        self.__group_thread_editor, self.__layout_thread_editor = create_v_group_box('Thread Config')
        self.__layout_thread_editor.addLayout(self.__label_thread_place_holder)

        # --------------------- Main layout ---------------------
        main_layout = QVBoxLayout()
        main_layout.addWidget(group_appearance)
        main_layout.addWidget(self.__group_thread_editor)
        self.setLayout(main_layout)

    def __create_thread_group_layout(self):
        layout = QVBoxLayout()
        line_width = QLineEdit()
        line_index = QLineEdit()
        radio_left = QRadioButton('Left')
        radio_right = QRadioButton('Right')
        button_browse = QPushButton('Browse')
        button_remove = QPushButton('Remove')

        layout.addLayout(horizon_layout([QLabel('Thread Layout: '), radio_left, radio_right,
                                         QLabel('Width'), line_width, button_remove]))
        layout.addLayout(horizon_layout([QLabel('Thread Index : '), line_index, button_browse]))
    

# ----------------------------------------------------- HistoryUi ------------------------------------------------------

class HistoryUi(QMainWindow):

    def __init__(self):
        super(HistoryUi, self).__init__()

        self.__menu_file = None
        self.__menu_view = None
        self.__menu_help = None

        self.__time_axis = TimeAxis()

        self.__init_ui()
        self.__init_menu()

    # ----------------------------- Setup and UI -----------------------------

    def __init_ui(self):
        self.setWindowTitle('SleepySoft/History - Sleepy')
        self.statusBar().showMessage('Ready')
        self.setCentralWidget(self.__time_axis)
        # self.showFullScreen()
        self.resize(1280, 800)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())

    def __init_menu(self):
        menu_bar = self.menuBar()

        self.__menu_file = menu_bar.addMenu('File')
        self.__menu_view = menu_bar.addMenu('View')
        self.__menu_help = menu_bar.addMenu('Help')

        # ----------------------- File -----------------------

        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit app')
        exit_action.triggered.connect(qApp.quit)
        self.__menu_file.addAction(exit_action)

        # ----------------------- View -----------------------

        action = QAction('&Historical Record Editor', self)
        action.setShortcut('Ctrl+R')
        action.setStatusTip('Open Historical Record Editor')
        action.triggered.connect(self.on_menu_record_editor)
        self.__menu_view.addAction(action)

        action = QAction('&History Record Filter Editor', self)
        action.setShortcut('Ctrl+R')
        action.setStatusTip('Open History Record Filter Editor')
        action.triggered.connect(self.on_menu_filter_editor)
        self.__menu_view.addAction(action)

        action = QAction('&History Thread Editor', self)
        action.setShortcut('Ctrl+T')
        action.setStatusTip('Open History Thread Editor')
        action.triggered.connect(self.on_menu_thread_editor)
        self.__menu_view.addAction(action)

        # ----------------------- Help -----------------------

        help_action = QAction('&Help', self)
        help_action.setShortcut('Ctrl+H')
        help_action.setStatusTip('Open help Window')
        help_action.triggered.connect(self.on_menu_help)
        self.__menu_help.addAction(help_action)

        about_action = QAction('&About', self)
        about_action.setShortcut('Ctrl+B')
        about_action.setStatusTip('Open about Window')
        about_action.triggered.connect(self.on_menu_about)
        self.__menu_help.addAction(about_action)

    # ----------------------------- UI Events -----------------------------

    def on_menu_record_editor(self):
        editor = HistoryEditorDialog()
        editor.exec()

    def on_menu_filter_editor(self):
        wnd = FilterEditor()
        dlg = WrapperQDialog(wnd)
        dlg.exec()

    def on_menu_thread_editor(self):
        wnd = AppearanceEditor()
        dlg = WrapperQDialog(wnd)
        dlg.exec()

    def on_menu_help(self):
        try:
            pass
            # import readme
            # help_wnd = InfoDialog('Help', readme.TEXT)
            # help_wnd.exec()
        except Exception as e:
            pass
        finally:
            pass

    def on_menu_about(self):
        try:
            pass
            # import readme
            # QMessageBox.about(self, 'About', readme.ABOUT)
        except Exception as e:
            pass
        finally:
            pass

    def on_menu_selected(self, docker):
        if docker is not None:
            if docker.isVisible():
                docker.hide()
            else:
                docker.show()

    def closeEvent(self, event):
        """Generate 'question' dialog on clicking 'X' button in title bar.
        Reimplement the closeEvent() event handler to include a 'Question'
        dialog with options on how to proceed - Save, Close, Cancel buttons
        """
        reply = QMessageBox.question(self,
                                     QtCore.QCoreApplication.translate('main', "退出"),
                                     QtCore.QCoreApplication.translate('main', "是否确认退出？"),
                                     QMessageBox.Close | QMessageBox.Cancel,
                                     QMessageBox.Cancel)
        if reply == QMessageBox.Close:
            sys.exit(0)
        else:
            pass


# ----------------------------------------------------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    main_wnd = HistoryUi()
    main_wnd.show()
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
