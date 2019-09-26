import sys
import traceback

from core import *


# --------------------------------------------------------------------------------------------------------------

# class EventIndex:
#     def __init__(self):
#         self.uuid = ''
#         self.since = 0.0
#         self.until = 0.0
#         self.event = None
#         self.abstract = ''
#
#         self.source = ''
#
#     def time(self) -> float:
#         return self.since
#
#     def adapt(self, since: float, until: float):
#         return (since < self.since < until) or (since < self.until < until)
#
#     def index_for(self, event):
#         self.source = event.source()
#
#         import core
#         event_time_list = event.time()
#         standard_time_list = core.TimeParser.standardize(','.join(event_time_list))
#
#         self.since = min(standard_time_list)
#         self.until = max(standard_time_list)
#
#         self.uuid = event.uuid()
#         self.event = event
#
#         if event.title() is not None and event.title().strip() != '':
#             self.abstract = event.title()
#         elif event.brief() is not None and event.brief().strip() != '':
#             self.abstract = event.brief()
#         elif event.event() is not None and event.event().strip() != '':
#             self.abstract = event.event()
#         self.abstract = self.abstract.strip()[:50]
#
#     def to_string(self) -> str:
#         text = '[START]: index\n'
#         text += 'uuid: """' + str(self.uuid) + '"""\n'
#         text += 'since: ' + str(self.since) + '\n'
#         text += 'until: ' + str(self.until) + '\n'
#         text += 'abstract: """' + str(self.abstract) + '"""\n'
#         text += 'source: """' + str(self.source) + '"""\n'
#         text += 'index: end\n\n'
#         return text
#
#     # ----------------------------------- print -----------------------------------
#
#         self.uuid = ''
#         self.since = 0.0
#         self.until = 0.0
#         self.event = None
#         self.abstract = ''
#
#         self.source = ''
#
#     def __str__(self):
#         return '---------------------------------------------------------------------------' + '\n' + \
#                 '|UUID     : ' + str(self.uuid) + '\n' + \
#                 '|SINCE    : ' + str(self.since) + '\n' + \
#                 '|UNTIL    : ' + str(self.until) + '\n' + \
#                 '|EVENT    : ' + str(self.event) + '\n' + \
#                 '|ABSTRACT : ' + str(self.abstract) + '\n' + \
#                 '---------------------------------------------------------------------------'


class RecordIndexer:
    def __init__(self):
        self.__indexes = []

    def reset(self):
        self.__indexes = []

    def get_indexes(self) -> list:
        return self.__indexes

    def index_path(self, directory: str):
        loader = HistoricalRecordLoader()
        his_filels = HistoricalRecordLoader.enumerate_local_path(directory)
        for his_file in his_filels:
            loader.from_file(his_file)
            records = loader.get_loaded_records()
            self.index_records(records)
            loader.restore()

    def index_records(self, records: list):
        for record in records:
            index = HistoricalRecord()
            index.index_for(record)
            self.__indexes.append(index)

    def replace_index_prefix(self, prefix_old: str, prefix_new: str):
        for index in self.__indexes:
            if index.source.startswith(prefix_old):
                index.source.replace(prefix_old, prefix_new)

    def dump_to_file(self, file: str):
        with open(file, 'wt', encoding='utf-8') as f:
            for index in self.__indexes:
                text = index.dump_record()
                f.write(text)

    def load_from_file(self, file: str):
        loader = HistoricalRecordLoader()
        loader.from_file(file)
        self.__indexes = loader.get_loaded_records()

        # parser = LabelTagParser()
        # with open(file, 'rt', encoding='utf-8') as f:
        #     text = f.read()
        #     parser.parse(text)
        #
        # index = None
        # label_tags = parser.get_label_tags()
        #
        # for label, tags in label_tags:
        #     if label == '[START]':
        #         index = EventIndex()
        #         continue
        #     if index is None:
        #         continue
        #     if label == 'uuid':
        #         index.uuid = tags[0]
        #     elif label == 'since':
        #         index.since = float(tags[0])
        #     elif label == 'until':
        #         index.until = float(tags[0])
        #     elif label == 'abstract':
        #         index.abstract = tags[0]
        #     elif label == 'source':
        #         index.source = tags[0]
        #     elif label == 'index':
        #         self.__indexes.append(index)
        #         index = None

    def print_indexes(self):
        for index in self.__indexes:
            print(index)


def test_load_index():
    indexer = RecordIndexer()
    indexer.load_from_file('history.index')
    indexer.print_indexes()


def main():
    indexer = RecordIndexer()
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            indexer.index_path(arg)
    else:
        depot_path = HistoricalRecordLoader.get_local_depot_path('China')
        indexer.index_path(depot_path)
    indexer.dump_to_file('history.index')

    test_load_index()


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


