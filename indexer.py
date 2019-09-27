import sys
import traceback

from core import *


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
                text = index.dump_record(True)
                f.write(text + '\n')

    def load_from_file(self, file: str):
        loader = HistoricalRecordLoader()
        loader.from_file(file)
        self.__indexes = loader.get_loaded_records()

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


