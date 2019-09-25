import traceback

from PyQt5.QtWidgets import QLineEdit, QAbstractItemView, QFileDialog, QCheckBox, QWidget, QLabel, QTextEdit, \
    QTabWidget, QComboBox, QGridLayout, QRadioButton

from core import *
from Utility.ui_utility import *


# ------------------------------------------------- class HistoryEditor ------------------------------------------------

class HistoryEditor(QWidget):
    def __init__(self, parent: QWidget):
        super(HistoryEditor, self).__init__(parent)

        self.__events = []
        self.__source = ''
        self.__current_event = None

        self.__tab_main = QTabWidget()
        # self.__combo_depot = QComboBox()
        self.__combo_events = QComboBox()

        self.__label_uuid = QLabel()
        self.__line_time = QLineEdit()
        self.__line_location = QLineEdit()
        self.__line_people = QLineEdit()
        self.__line_organization = QLineEdit()
        self.__line_default_tags = QLineEdit()

        self.__button_auto_time = QPushButton('Auto Detect')
        self.__button_auto_location = QPushButton('Auto Detect')
        self.__button_auto_people = QPushButton('Auto Detect')
        self.__button_auto_organization = QPushButton('Auto Detect')

        self.__radio_time = QRadioButton('Time')
        self.__radio_location = QRadioButton('Location')
        self.__radio_people = QRadioButton('Participant')
        self.__radio_organization = QRadioButton('Organization')
        self.__radio_event = QRadioButton('Event')

        self.__check_time = QCheckBox('Lock')
        self.__check_location = QCheckBox('Lock')
        self.__check_people = QCheckBox('Lock')
        self.__check_organization = QCheckBox('Lock')
        self.__check_default_tags = QCheckBox('Lock')

        self.__line_title = QLineEdit()
        self.__text_brief = QTextEdit()
        self.__text_event = QTextEdit()

        self.__table_tags = EasyQTableWidget()

        self.__button_new = QPushButton('New Event')
        self.__button_new_file = QPushButton('New File')
        self.__button_apply = QPushButton('Apply')
        self.__button_cancel = QPushButton('Cancel')

        self.init_ui()
        self.config_ui()

    def init_ui(self):
        root_layout = QVBoxLayout()

        line = QHBoxLayout()
        line.addWidget(self.__combo_events, 1)
        line.addWidget(self.__button_new, 0)
        line.addWidget(self.__button_new_file, 0)

        root_layout.addLayout(line)
        root_layout.addWidget(self.__tab_main)
        root_layout.addLayout(horizon_layout([self.__button_apply, self.__button_cancel]))
        self.setLayout(root_layout)

        event_page_layout = create_new_tab(self.__tab_main, 'Event Editor')

        property_layout = QGridLayout()

        property_layout.addWidget(QLabel('Event ID'), 0, 0)
        property_layout.addWidget(self.__label_uuid, 0, 1)

        property_layout.addWidget(QLabel('Event Tags'), 1, 0)
        property_layout.addWidget(self.__line_default_tags, 1, 1, 1, 2)
        property_layout.addWidget(self.__check_default_tags, 1, 3)

        # property_layout.addWidget(QLabel('Event Time'), 1, 0)
        property_layout.addWidget(self.__radio_time, 2, 0)
        property_layout.addWidget(self.__line_time, 2, 1)
        property_layout.addWidget(self.__button_auto_time, 2, 2)
        property_layout.addWidget(self.__check_time, 2, 3)

        # property_layout.addWidget(QLabel('Event Location'), 2, 0)
        property_layout.addWidget(self.__radio_location, 3, 0)
        property_layout.addWidget(self.__line_location, 3, 1)
        property_layout.addWidget(self.__button_auto_location, 3, 2)
        property_layout.addWidget(self.__check_location, 3, 3)

        # property_layout.addWidget(QLabel('Event Participant'), 3, 0)
        property_layout.addWidget(self.__radio_people, 4, 0)
        property_layout.addWidget(self.__line_people, 4, 1)
        property_layout.addWidget(self.__button_auto_people, 4, 2)
        property_layout.addWidget(self.__check_people, 4, 3)

        # property_layout.addWidget(QLabel('Event Organization'), 4, 0)
        property_layout.addWidget(self.__radio_organization, 5, 0)
        property_layout.addWidget(self.__line_organization, 5, 1)
        property_layout.addWidget(self.__button_auto_organization, 5, 2)
        property_layout.addWidget(self.__check_organization, 5, 3)

        self.__radio_event.setChecked(True)
        property_layout.addWidget(self.__radio_event, 6, 0)

        event_page_layout.addLayout(property_layout)

        group, layout = create_v_group_box('')
        event_page_layout.addWidget(group)

        layout.addWidget(QLabel('Event Title'))
        layout.addWidget(self.__line_title)

        layout.addWidget(QLabel('Event Brief'))
        layout.addWidget(self.__text_brief, 2)

        layout.addWidget(QLabel('Event Description'))
        layout.addWidget(self.__text_event, 5)

        layout = create_new_tab(self.__tab_main, 'Label Tag Editor')
        layout.addWidget(self.__table_tags)

        self.setMinimumSize(700, 500)

    def config_ui(self):
        self.__button_auto_time.clicked.connect(self.on_button_auto_time)
        self.__button_auto_location.clicked.connect(self.on_button_auto_location)
        self.__button_auto_people.clicked.connect(self.on_button_auto_people)
        self.__button_auto_organization.clicked.connect(self.on_button_auto_organization)

        self.__button_new.clicked.connect(self.on_button_new)
        self.__button_new_file.clicked.connect(self.on_button_file)
        self.__button_apply.clicked.connect(self.on_button_apply)
        self.__button_cancel.clicked.connect(self.on_button_cancel)

    def update_combo_events(self):
        index = -1
        self.__combo_events.clear()
        for i in range(0, len(self.__events)):
            event = self.__events[i]
            self.__combo_events.addItem(event.uuid())
            if event == self.__current_event:
                index = i
        if index >= 0:
            self.__combo_events.setCurrentIndex(index)
        else:
            print('Cannot find the current event in combobox.')

    # ---------------------------------------------------- Features ----------------------------------------------------

    def load_event(self, event: History.Event):
        self.__label_uuid.setText(LabelTagParser.tags_to_text(event.uuid()))
        self.__line_time.setText(LabelTagParser.tags_to_text(event.time()))

        self.__line_location.setText(LabelTagParser.tags_to_text(event.tags('location')))
        self.__line_people.setText(LabelTagParser.tags_to_text(event.tags('people')))
        self.__line_organization.setText(LabelTagParser.tags_to_text(event.tags('location')))
        self.__line_default_tags.setText(LabelTagParser.tags_to_text(event.tags('tags')))

        self.__line_title.setText(LabelTagParser.tags_to_text(event.title()))
        self.__text_brief.setText(LabelTagParser.tags_to_text(event.brief()))
        self.__text_event.setText(LabelTagParser.tags_to_text(event.event()))

    def set_events(self, events: History.Event or [History.Event], source: str):
        self.__events = events if isinstance(events, list) else [events]
        self.__current_event = self.__events[0]
        self.__source = source
        self.update_combo_events()

    def get_event(self) -> History.Event:
        return self.__events

    # ---------------------------------------------------- UI Event ----------------------------------------------------

    def on_button_auto_time(self):
        pass

    def on_button_auto_location(self):
        pass

    def on_button_auto_people(self):
        pass

    def on_button_auto_organization(self):
        pass

    def on_button_new(self):
        self.create_new_event()

    def on_button_file(self):
        self.create_new_file()

    def on_button_apply(self):
        if self.__current_event is None:
            self.__current_event = History.Event()
        else:
            self.__current_event.reset()

        self.ui_to_current_event()

        result = False
        if len(self.__events) == 0:
            source = str(self.__current_event.uuid()) + '.his'
            result = History.Loader().to_local_depot(
                self.__current_event, 'China', source)
        else:
            # The whole file should be updated
            if self.__current_event not in self.__events:
                self.__events.append(self.__current_event)
            source = self.__events[0].source()
            if source is None or len(source) == 0:
                source = str(self.__current_event.uuid()) + '.his'
                result = History.Loader().to_local_depot(self.__events, 'China', source)

        tips = 'Save Successful.' if result else 'Save Fail.'
        if len(source) > 0:
            tips += '\nSave File: ' + source
        QMessageBox.information(self, 'Save', tips, QMessageBox.Ok)

    def on_button_cancel(self):
        if self.parent() is not None:
            self.parent().close()
        else:
            self.close()

    # --------------------------------------------------- Operation ----------------------------------------------------

    def ui_to_current_event(self, only_locked: bool = False):
        """
        UI data to current event.
        :param only_locked: Only used for keeping the locked data. Pass True to enable this feature.
        :return:
        """
        input_time = self.__line_time.text()
        input_location = self.__line_location.text()
        input_people = self.__line_people.text()
        input_organization = self.__line_organization.text()
        input_default_tags = self.__line_default_tags.text()

        lock_time = self.__check_time.isChecked()
        lock_location = self.__check_location.isChecked()
        lock_people = self.__check_people.isChecked()
        lock_organization = self.__check_organization.isChecked()
        lock_default_tags = self.__check_default_tags.isChecked()

        input_title = self.__line_title.text()
        input_brief = self.__text_brief.toPlainText()
        input_event = self.__text_event.toPlainText()

        if not only_locked or lock_time:
            self.__current_event.set_label_tags('time',         input_time.split(','))
        if not only_locked or lock_location:
            self.__current_event.set_label_tags('location',     input_location.split(','))
        if not only_locked or lock_people:
            self.__current_event.set_label_tags('people',       input_people.split(','))
        if not only_locked or lock_organization:
            self.__current_event.set_label_tags('organization', input_organization.split(','))
        if not only_locked or lock_default_tags:
            self.__current_event.set_label_tags('tags',         input_default_tags.split(','))

        if not only_locked:
            self.__current_event.set_label_tags('title', input_title)
            self.__current_event.set_label_tags('brief', input_brief)
            self.__current_event.set_label_tags('event', input_event)

    def create_new_event(self):
        if self.__current_event is not None:
            # TODO:
            pass
        self.__current_event = History.Event()
        self.__events.append(self.__current_event)
        self.ui_to_current_event(True)
        self.load_event(self.__current_event)
        self.update_combo_events()

    def create_new_file(self):
        self.create_new_event()
        self.__source = str(self.__current_event.uuid()) + '.his'

    def save_events(self):
        result = History.Loader().to_local_depot(self.__events, 'China', self.__source)
        tips = 'Save Successful.' if result else 'Save Fail.'
        tips += '\nSave File: ' + self.__source
        QMessageBox.information(None, 'Save', tips, QMessageBox.Ok)


# --------------------------------------------- class HistoryEditorDialog ----------------------------------------------

class HistoryEditorDialog(QDialog):
    def __init__(self):
        super(HistoryEditorDialog, self).__init__()
        self.history_editor = HistoryEditor(self)
        layout = QVBoxLayout()
        layout.addWidget(self.history_editor)
        self.setLayout(layout)

    def get_history_editor(self) -> HistoryEditor:
        return self.history_editor


# ------------------------------------------------ File Entry : main() -------------------------------------------------

def main():
    app = QApplication(sys.argv)
    HistoryEditorDialog().exec()


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



