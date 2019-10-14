#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from functools import partial
from types import SimpleNamespace

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QWidget, QPushButton, \
    QDockWidget, QAction, qApp, QMessageBox, QDialog, QVBoxLayout, QLabel, QGroupBox, QBoxLayout, QTableWidget, \
    QTableWidgetItem, QTabWidget, QLayout, QTextEdit, QListWidget, QListWidgetItem


# -------------------------------------------------------------------------------------------------------

def horizon_layout(widgets: list) -> QHBoxLayout:
    layout = QHBoxLayout()
    for widget in widgets:
        layout.addWidget(widget)
    return layout


def create_v_group_box(title: str) -> (QGroupBox, QBoxLayout):
    group_box = QGroupBox(title)
    group_layout = QVBoxLayout()
    # group_layout.addStretch(1)
    group_box.setLayout(group_layout)
    return group_box, group_layout


def create_new_tab(tab_widget: QTabWidget, title: str, layout: QLayout = None) -> QLayout:
    empty_wnd = QWidget()
    wnd_layout = layout if layout is not None else QVBoxLayout()
    empty_wnd.setLayout(wnd_layout)
    tab_widget.addTab(empty_wnd, title)
    return wnd_layout


def restore_text_editor(editor: QTextEdit):
    editor.clear()
    editor.setFocus()
    font = QFont()
    font.setFamily("微软雅黑")
    font.setPointSize(10)
    editor.selectAll()
    editor.setCurrentFont(font)
    editor.setTextColor(Qt.black)
    editor.setTextBackgroundColor(Qt.white)


# =========================================== InfoDialog ===========================================

class InfoDialog(QDialog):
    def __init__(self, title, text):
        super().__init__()
        self.__text = text
        self.__title = title
        self.__button_ok = QPushButton('OK')
        self.__layout_main = QVBoxLayout()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.__title)
        self.__button_ok.clicked.connect(self.on_btn_click_ok)
        self.__layout_main.addWidget(QLabel(self.__text), 1)
        self.__layout_main.addWidget(self.__button_ok)
        self.setLayout(self.__layout_main)

    def on_btn_click_ok(self):
        self.close()


# =========================================== CommonMainWindow ===========================================

class CommonMainWindow(QMainWindow):

    def __init__(self):
        super(CommonMainWindow, self).__init__()
        self.__menu_view = None
        self.__sub_window_list = []
        self.common_init_ui()
        self.common_init_menu()
        # self.init_sub_window()

    # ----------------------------- Setup and UI -----------------------------

    def common_init_ui(self):
        self.setWindowTitle('Common Main Window - Sleepy')
        self.statusBar().showMessage('Ready')
        # self.showFullScreen()
        self.resize(1280, 800)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())

    def common_init_menu(self):
        menu_bar = self.menuBar()

        menu_file = menu_bar.addMenu('File')
        self.__menu_view = menu_bar.addMenu('View')
        menu_help = menu_bar.addMenu('Help')

        exit_action = QAction('&Exit', self)
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

    # def init_sub_window(self):
        # self.__add_sub_window(self.__serial_port_module, {
        #     'DockName': self.__translate('main', ''),
        #     'DockArea': Qt.LeftDockWidgetArea,
        #     'DockShow': True,
        #     'DockFloat': True,
        #     'MenuName': self.__translate('main', ''),
        #     'MenuPresent': True,
        #     'ActionName': self.__translate('main', ''),
        #     'ActionShortcut': self.__translate('main', 'Ctrl+S'),
        #     'ActionPresent': True,
        #     'ActionTips': self.__translate('main', ''),
        # })

    def add_sub_window(self, window: QWidget, config: dict):
        sub_window_data = SimpleNamespace()
        sub_window_data.config = config
        self.__setup_sub_window_dock(window, config, sub_window_data)
        self.__setup_sub_window_menu(config, sub_window_data)
        self.__setup_sub_window_action(config, sub_window_data)

    def __setup_sub_window_dock(self, window: QWidget, config: dict, sub_window_data: SimpleNamespace):
        dock_name = config.get('DockName', '')
        dock_area = config.get('DockArea', Qt.NoDockWidgetArea)
        dock_show = config.get('DockShow', False)
        dock_float = config.get('DockFloat', False)

        dock_wnd = QDockWidget(dock_name, self)
        self.addDockWidget(dock_area, dock_wnd)

        dock_wnd.setWidget(window)
        if dock_float:
            dock_wnd.setFloating(True)
            dock_wnd.move(self.geometry().center() - dock_wnd.rect().center())
        if dock_show:
            dock_wnd.show()

        sub_window_data.dock_wnd = dock_wnd

    def __setup_sub_window_menu(self, config: dict, sub_window_data: SimpleNamespace):
        dock_name = config.get('DockName', '')
        menu_name = config.get('MenuName', dock_name)
        menu_present = config.get('MenuPresent', False)
        dock_wnd = sub_window_data.dock_wnd if hasattr(sub_window_data, 'dock_wnd') else None

        if menu_present and dock_wnd is not None:
            menu_view = self.__menu_view
            menu_entry = menu_view.addAction(menu_name)
            menu_entry.triggered.connect(partial(self.on_menu_selected, dock_wnd))
            sub_window_data.menu_entry = menu_entry
        else:
            sub_window_data.menu_entry = None

    def __setup_sub_window_action(self, config: dict, sub_window_data: SimpleNamespace):
        dock_name = config.get('DockName', '')
        action_name = config.get('ActionName', dock_name)
        action_shortcut = config.get('ActionShortcut', '')
        action_present = config.get('ActionPresent', False)
        action_tips = config.get('ActionTips', '')
        dock_wnd = sub_window_data.dock_wnd if hasattr(sub_window_data, 'dock_wnd') else None
        # menu_entry = sub_window_data.menu_entry if hasattr(sub_window_data, 'menu_entry') else None

        if action_present and dock_wnd is not None:
            action = QAction(action_name, self)
            if action_shortcut != '':
                action.setShortcut(action_shortcut)
            action.setStatusTip(action_tips)
            action.triggered.connect(partial(self.on_menu_selected, dock_wnd))
            # if menu_entry is not None:
            #     menu_entry.addAction(action)
        else:
            sub_window_data.menu_entry = None

    # ----------------------------- UI Events -----------------------------

    def on_menu_help(self):
        try:
            import readme
            help_wnd = InfoDialog('Help', readme.TEXT)
            help_wnd.exec()
        except Exception as e:
            pass
        finally:
            pass

    def on_menu_about(self):
        try:
            import readme
            QMessageBox.about(self, 'About', readme.ABOUT)
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


# =========================================== EasyQTableWidget ===========================================

class EasyQTableWidget(QTableWidget):
    def __init__(self, *__args):
        super(EasyQTableWidget, self).__init__(*__args)

    def AppendRow(self, content: [str]):
        row_count = self.rowCount()
        self.insertRow(row_count)
        for col in range(0, len(content)):
            self.setItem(row_count, col, QTableWidgetItem(content[col]))

    def GetCurrentRow(self) -> [str]:
        row_index = self.GetCurrentIndex()
        if row_index == -1:
            return []
        return [self.model().index(row_index, col_index).data() for col_index in range(self.columnCount())]

    def GetCurrentIndex(self) -> int:
        return self.selectionModel().currentIndex().row() if self.selectionModel().hasSelection() else -1


# =========================================== EasyQListSuite ===========================================

class EasyQListSuite(QWidget):
    def __init__(self, *__args):
        super(EasyQListSuite, self).__init__(*__args)

        self.__item_list = []

        self.__list_main = QListWidget(self)
        self.__button_add = QPushButton('Add')
        self.__button_remove = QPushButton('Remove')

        self.__init_ui()
        self.__config_ui()

    def update_item(self, items: [(str, any)]):
        self.__item_list.clear()
        for item in items:
            if isinstance(item, (list, tuple)):
                if len(item) == 0:
                    continue
                elif len(item) == 1:
                    self.__item_list.append((str(item[0]), item[0]))
                else:
                    self.__item_list.append((str(item[0]), item[1]))
            else:
                self.__item_list.append((str(item), item))
        self.__update_list()

    def get_select_items(self) -> [any]:
        return [item.data(Qt.UserRole) for item in self.__list_main.selectedItems()]

    def set_add_handler(self, handler):
        self.__button_add.clicked.connect(handler)

    def set_remove_handler(self, handler):
        self.__button_remove.clicked.connect(handler)

    # ---------------------------------------- Private ----------------------------------------

    def __init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        line_layout = QHBoxLayout()
        line_layout.addWidget(self.__button_add)
        line_layout.addWidget(self.__button_remove)

        main_layout.addWidget(self.__list_main)
        main_layout.addLayout(line_layout)

    def __config_ui(self):
        pass
        # self.__button_add.clicked.connect(self.__on_btn_click_add)
        # self.__button_remove.clicked.connect(self.__on_btn_click_remove)

    def __update_list(self):
        self.__list_main.clear()
        for text, obj in self.__item_list:
            item = QListWidgetItem()
            item.setText(text)
            item.setData(Qt.UserRole, obj)
            self.__list_main.addItem(item)

    def __on_btn_click_add(self):
        pass

    def __on_btn_click_remove(self):
        pass













