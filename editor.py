import traceback

from PyQt5.QtWidgets import QLineEdit, QAbstractItemView, QFileDialog, QCheckBox, QWidget, QLabel, QTextEdit, \
    QTabWidget, QComboBox, QGridLayout

from core import *
from Utility.ui_utility import *


class HistoryEditor(QWidget):
    def __init__(self):
        super(HistoryEditor, self).__init__()

        self.__tab_main = QTabWidget()
        self.__combo_stories = QComboBox()

        self.__label_uuid = QLabel()
        self.__line_time = QLineEdit()
        self.__line_location = QLineEdit()
        self.__line_people = QLineEdit()
        self.__line_organization = QLineEdit()

        self.__button_auto_time = QPushButton('Auto Detect')
        self.__button_auto_location = QPushButton('Auto Detect')
        self.__button_auto_people = QPushButton('Auto Detect')
        self.__button_auto_organization = QPushButton('Auto Detect')

        self.__line_title = QLineEdit()
        self.__text_brief = QTextEdit()
        self.__text_event = QTextEdit()

        self.__table_tags = EasyQTableWidget()

        self.__button_apply = QPushButton('Apply')
        self.__button_cancel = QPushButton('Cancel')

        self.init_ui()
        self.config_ui()

    def init_ui(self):
        root_layout = QVBoxLayout()
        root_layout.addWidget(self.__combo_stories)
        root_layout.addWidget(self.__tab_main)
        root_layout.addLayout(horizon_layout([self.__button_apply, self.__button_cancel]))
        self.setLayout(root_layout)

        event_page_layout = create_new_tab(self.__tab_main, 'Event Editor')

        property_layout = QGridLayout()

        property_layout.addWidget(QLabel('Event ID'), 0, 0)
        property_layout.addWidget(self.__label_uuid, 0, 1)

        property_layout.addWidget(QLabel('Event Time'), 1, 0)
        property_layout.addWidget(self.__line_time, 1, 1)
        property_layout.addWidget(self.__button_auto_time, 1, 2)

        property_layout.addWidget(QLabel('Event Time'), 2, 0)
        property_layout.addWidget(self.__line_location, 2, 1)
        property_layout.addWidget(self.__button_auto_location, 2, 2)

        property_layout.addWidget(QLabel('Event Participant'), 3, 0)
        property_layout.addWidget(self.__line_people, 3, 1)
        property_layout.addWidget(self.__button_auto_people, 3, 2)

        property_layout.addWidget(QLabel('Event Organization'), 4, 0)
        property_layout.addWidget(self.__line_organization, 4, 1)
        property_layout.addWidget(self.__button_auto_organization, 4, 2)

        event_page_layout.addLayout(property_layout)

        event_page_layout.addWidget(QLabel('Event Title'))
        event_page_layout.addWidget(self.__line_title)

        event_page_layout.addWidget(QLabel('Event Brief'))
        event_page_layout.addWidget(self.__text_brief, 2)

        event_page_layout.addWidget(QLabel('Event Description'))
        event_page_layout.addWidget(self.__text_event, 5)

        ltags_page_layout = create_new_tab(self.__tab_main, 'Label Tag Editor')
        ltags_page_layout.addWidget(self.__table_tags)

    def config_ui(self):
        self.__button_auto_time.clicked.connect(self.on_button_auto_time)
        self.__button_auto_location.clicked.connect(self.on_button_auto_location)
        self.__button_auto_people.clicked.connect(self.on_button_auto_people)
        self.__button_auto_organization.clicked.connect(self.on_button_auto_organization)

    # ---------------------------------------------------- Features ----------------------------------------------------

    def load_event(self, event: History.Event):
        self.__label_uuid.setText(event.uuid())
        self.__line_time.setText(event.time())

        self.__line_location.setText(event.tags('location'))
        self.__line_people.setText(event.tags('people'))
        self.__line_organization.setText(event.tags('location'))

        self.__line_title.setText(event.title())
        self.__text_brief.setText(event.brief())
        self.__text_event.setText(event.event())

    # ---------------------------------------------------- UI Event ----------------------------------------------------

    def on_button_auto_time(self):
        pass

    def on_button_auto_location(self):
        pass

    def on_button_auto_people(self):
        pass

    def on_button_auto_organization(self):
        pass


def main():
    app = QApplication(sys.argv)

    layout = QVBoxLayout()
    layout.addWidget(HistoryEditor())

    dlg = QDialog()
    dlg.setLayout(layout)
    dlg.exec()


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



