import traceback

from PyQt5.QtWidgets import QLineEdit, QAbstractItemView, QFileDialog, QCheckBox, QWidget, QLabel, QTextEdit, \
    QTabWidget, QComboBox, QGridLayout, QRadioButton

from core import *
from Utility.ui_utility import *


# ------------------------------------------------- class HistoryEditor ------------------------------------------------

class HistoryEditor(QWidget):

    class Agent:
        def __init__(self):
            pass

        def on_apply(self):
            pass

        def on_cancel(self):
            pass

    def __init__(self, parent: QWidget):
        super(HistoryEditor, self).__init__(parent)

        self.__records = []
        self.__source = ''
        self.__current_record = None
        self.__operation_agents = []

        self.__ignore_combo = False

        self.__tab_main = QTabWidget()
        # self.__combo_depot = QComboBox()
        self.__combo_records = QComboBox()

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
        self.__radio_record = QRadioButton('Event')

        self.__check_time = QCheckBox('Lock')
        self.__check_location = QCheckBox('Lock')
        self.__check_people = QCheckBox('Lock')
        self.__check_organization = QCheckBox('Lock')
        self.__check_default_tags = QCheckBox('Lock')

        self.__line_title = QLineEdit()
        self.__text_brief = QTextEdit()
        self.__text_record = QTextEdit()

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
        line.addWidget(self.__combo_records, 1)
        line.addWidget(self.__button_new, 0)
        line.addWidget(self.__button_new_file, 0)

        root_layout.addLayout(line)
        root_layout.addWidget(self.__tab_main)
        root_layout.addLayout(horizon_layout([self.__button_apply, self.__button_cancel]))
        self.setLayout(root_layout)

        record_page_layout = create_new_tab(self.__tab_main, 'Event Editor')

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

        self.__radio_record.setChecked(True)
        property_layout.addWidget(self.__radio_record, 6, 0)

        record_page_layout.addLayout(property_layout)

        group, layout = create_v_group_box('')
        record_page_layout.addWidget(group)

        layout.addWidget(QLabel('Event Title'))
        layout.addWidget(self.__line_title)

        layout.addWidget(QLabel('Event Brief'))
        layout.addWidget(self.__text_brief, 2)

        layout.addWidget(QLabel('Event Description'))
        layout.addWidget(self.__text_record, 5)

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

        self.__combo_records.currentIndexChanged.connect(self.on_combo_records)

    def update_combo_records(self):
        index = -1
        self.__ignore_combo = True
        self.__combo_records.clear()
        for i in range(0, len(self.__records)):
            record = self.__records[i]
            self.__combo_records.addItem(record.uuid())
            if record == self.__current_record:
                index = i
        if index >= 0:
            self.__combo_records.setCurrentIndex(index)
        else:
            print('Cannot find the current record in combobox.')
        self.__ignore_combo = False

    # ---------------------------------------------------- Features ----------------------------------------------------

    def add_agent(self, agent):
        self.__operation_agents.append(agent)

    def edit_source(self, source: str, current_uuid: str) -> bool:
        # TODO: Do we need this?
        loader = HistoricalRecordLoader()
        if not loader.from_source(source):
            return False
        self.__source = source
        self.__records = loader.get_loaded_records()
        self.__current_record = None
        for record in self.__records:
            if record.uuid() == current_uuid:
                self.__current_record = record
                break
        if self.__current_record is None:
            self.__current_record = HistoricalRecord()
        self.update_combo_records()
        self.load_record(self.__current_record)

    def load_record(self, record: HistoricalRecord or str):
        # if isinstance(record, str):
        #     for r in self.__records:
        #         if r.uuid() == record:
        #             record = r
        #             break
        # if isinstance(record, str):
        #     print('Cannot load record for uuid: ' + record)
        #     return

        self.__label_uuid.setText(LabelTagParser.tags_to_text(record.uuid()))
        self.__line_time.setText(LabelTagParser.tags_to_text(record.time()))

        self.__line_location.setText(LabelTagParser.tags_to_text(record.get_tags('location')))
        self.__line_people.setText(LabelTagParser.tags_to_text(record.get_tags('people')))
        self.__line_organization.setText(LabelTagParser.tags_to_text(record.get_tags('location')))
        self.__line_default_tags.setText(LabelTagParser.tags_to_text(record.get_tags('tags')))

        self.__line_title.setText(LabelTagParser.tags_to_text(record.title()))
        self.__text_brief.setText(LabelTagParser.tags_to_text(record.brief()))
        self.__text_record.setText(LabelTagParser.tags_to_text(record.event()))

    def set_records(self, records: HistoricalRecord or [HistoricalRecord], source: str):
        self.__records = records if isinstance(records, list) else [records]
        self.__current_record = self.__records[0]
        self.__source = source
        self.update_combo_records()

    def get_source(self) -> str:
        return self.__source

    def get_records(self) -> [HistoricalRecord]:
        return self.__records

    def get_current_record(self) -> HistoricalRecord:
        return self.__current_record

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
        self.create_new_record()

    def on_button_file(self):
        self.create_new_file()

    def on_button_apply(self):
        if self.__current_record is None:
            self.__current_record = HistoricalRecord()
            self.__records.append(self.__current_record)
        else:
            self.__current_record.reset()
        self.ui_to_current_record()

        for agent in self.__operation_agents:
            agent.on_apply()

    def on_button_cancel(self):
        for agent in self.__operation_agents:
            agent.on_cancel()

    def on_combo_records(self):
        if self.__ignore_combo:
            return

        _uuid = self.__combo_records.currentText()
        record = self.__look_for_record(_uuid)

        if record is None:
            print('Cannot find record for uuid: ' + _uuid)
            return

        self.__current_record = record
        self.load_record(record)

    # --------------------------------------------------- Operation ----------------------------------------------------

    def ui_to_current_record(self, only_locked: bool = False):
        """
        UI data to current record.
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
        input_event = self.__text_record.toPlainText()

        if not only_locked or lock_time:
            self.__current_record.set_label_tags('time',         input_time.split(','))
        if not only_locked or lock_location:
            self.__current_record.set_label_tags('location',     input_location.split(','))
        if not only_locked or lock_people:
            self.__current_record.set_label_tags('people',       input_people.split(','))
        if not only_locked or lock_organization:
            self.__current_record.set_label_tags('organization', input_organization.split(','))
        if not only_locked or lock_default_tags:
            self.__current_record.set_label_tags('tags',         input_default_tags.split(','))

        if not only_locked:
            self.__current_record.set_label_tags('title', input_title)
            self.__current_record.set_label_tags('brief', input_brief)
            self.__current_record.set_label_tags('event', input_event)

    def create_new_record(self):
        if self.__current_record is not None:
            # TODO:
            pass
        self.__current_record = HistoricalRecord()
        self.__records.append(self.__current_record)
        self.ui_to_current_record(True)
        self.load_record(self.__current_record)
        self.update_combo_records()

    def create_new_file(self):
        self.create_new_record()
        self.__source = str(self.__current_record.uuid()) + '.his'

    def save_records(self):
        result = History.Loader().to_local_depot(self.__records, 'China', self.__source)
        tips = 'Save Successful.' if result else 'Save Fail.'
        tips += '\nSave File: ' + self.__source
        QMessageBox.information(None, 'Save', tips, QMessageBox.Ok)

    # ------------------------------------------------------------------------------

    def __look_for_record(self, _uuid: str):
        for record in self.__records:
            if record.uuid() == _uuid:
                return record
        return None


# --------------------------------------------- class HistoryEditorDialog ----------------------------------------------

class HistoryEditorDialog(QDialog):
    def __init__(self, editor_agent: HistoryEditor.Agent = None):
        super(HistoryEditorDialog, self).__init__()

        self.history_editor = HistoryEditor(self)
        self.history_editor.add_agent(editor_agent if editor_agent is not None else self)

        layout = QVBoxLayout()
        layout.addWidget(self.history_editor)

        self.setLayout(layout)
        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowMinMaxButtonsHint |
                            QtCore.Qt.WindowSystemMenuHint)

    def get_history_editor(self) -> HistoryEditor:
        return self.history_editor

    # ------------------------------- HistoryEditor.Agent -------------------------------

    def on_apply(self):
        source = self.history_editor.get_source()
        records = self.history_editor.get_records()

        if records is None or len(records) == 0:
            return

        if source is None or source == '':
            source = records[0].source()
        if source is None or source == '':
            source = records[0].uuid() + '.his'

        # TODO: Select depot
        result = HistoricalRecordLoader.to_local_depot(records, 'China', source)

        # result = False
        # if len(self.__records) == 0:
        #     source = str(self.__current_record.uuid()) + '.his'
        # else:
        #     # The whole file should be updated
        #     if self.__current_record not in self.__records:
        #         self.__records.append(self.__current_record)
        #     source = self.__records[0].source()
        #     if source is None or len(source) == 0:
        #         source = str(self.__current_record.uuid()) + '.his'
        #         result = History.Loader().to_local_depot(self.__records, 'China', source)

        tips = 'Save Successful.' if result else 'Save Fail.'
        if len(source) > 0:
            tips += '\nSave File: ' + source
        QMessageBox.information(self, 'Save', tips, QMessageBox.Ok)

    def on_cancel(self):
        self.close()


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



