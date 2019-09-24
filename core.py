import os
import string
import uuid
from os import sys, path, listdir


# ------------------------------------------------------ Compare ------------------------------------------------------
import traceback


def list_unique(list1: list) -> list:
    return list(set(list1))


def list_union_unique(list1: list, list2: list) -> list:
    return list(set(list1).union(set(list2)))


def compare_intersection(list1, list2) -> bool:
    return len(list(set(list1).intersection(set(list2)))) > 0


def check_normalize_expects(expects: list) -> list or None:
    """
    Make expects as a list.
    :param expects: The parameter that need to be normalized
    :return: None if the expects is invalid.
    """
    if expects is None:
        return None
    if isinstance(expects, (list, tuple)):
        if len(expects) == 0:
            return None
        return expects
    else:
        return [expects]


def check_condition_range(conditions: dict, key: str, expects: list) -> bool:
    expects = check_normalize_expects(expects)
    if expects is None:
        return True
    value = conditions.get(key, None)
    if value is None:
        return True
    lower = min(expects)
    upper = max(expects)
    if isinstance(value, (list, tuple)):
        for v in value:
            if v < lower or v > upper:
                return False
        return True
    else:
        return lower < value < upper


def check_condition_within(conditions: dict, key: str, expects: list) -> bool:
    expects = check_normalize_expects(expects)
    if expects is None:
        return True
    value = conditions.get(key, None)
    if value is None:
        return True
    if not isinstance(value, (list, tuple)):
        return value in expects
    else:
        return compare_intersection(value, expects)


# ---------------------------------------------------- Token Parser ----------------------------------------------------

# TODO: Use NLP to process nature language

class TimeParser:
    def __init__(self):
        print('Instance TimeParser is not necessary.')

    SEPARATOR = [
        '-',
        ','
    ]

    PREFIX_CE = [
        'ac',
        'ce',
        'common era',
        '公元',
        '距今',
    ]

    PREFIX_BCE = [
        'bc',
        'bce',
        'before common era',
        '公元前',
        '距今',
    ]

    @staticmethod
    def standardize(time_str: str) -> [float]:
        unified_time_str = time_str
        for i in range(1, len(TimeParser.SEPARATOR)):
            unified_time_str = unified_time_str.replace(TimeParser.SEPARATOR[i], TimeParser.SEPARATOR[0])

        time_list = []
        sub_time_str_list = unified_time_str.split(TimeParser.SEPARATOR[0])
        for sub_time_str in sub_time_str_list:
            try:
                num = TimeParser.parse_single_time_str(sub_time_str)
                time_list.append(num)
            except Exception as e:
                print('Parse time error: ' + sub_time_str + ' -> ' + str(e))
            finally:
                pass
        return time_list

    @staticmethod
    def parse_single_time_str(time_str: str) -> float:
        if time_str.lower().startswith(tuple(TimeParser.PREFIX_BCE)):
            sign = -1
        elif time_str.lower().startswith(tuple(TimeParser.PREFIX_CE)):
            sign = 1
        else:
            sign = 1
        # non_numeric_chars = ''.join(set(string.printable) - set(string.digits))
        number_str = int("".join(filter(str.isdigit, time_str)))
        # number_str = time_str.translate(non_numeric_chars)
        return sign * float(number_str)


# ---------------------------------------------------- Token Parser ----------------------------------------------------

class TokenParser:
    def __init__(self):
        self.__text = ''
        self.__tokens = []
        self.__wrappers = []                  # [(start, close)]
        self.__space_tokens = [' ']
        self.__escape_symbols = []

        self.__mark_idx = 0
        self.__parse_idx = 0

        self.__meet_token = ''

        self.__in_wrapper = False
        self.__wrapper_index = -1

    # ========================================== Config parser ==========================================

    def config(self, tokens: list, wrappers: list, escape_symbols: list):
        self.__tokens = tokens
        self.__wrappers = wrappers
        self.__escape_symbols = escape_symbols

        for wrapper in wrappers:
            if not isinstance(wrapper, (list, tuple)) or len(wrapper) != 2:
                print('Error wrapper format. Its format should be: [(start, close)], ...')
            for token in wrapper:
                if token not in self.__tokens:
                    self.__tokens.append(token)

    def reset(self):
        self.__mark_idx = 0
        self.__parse_idx = 0

        self.__in_wrapper = False
        self.__wrapper_index = -1

    def attach(self, text: str):
        self.__text = text
        self.__mark_idx = 0
        self.__parse_idx = 0

    # ========================================== Parse ==========================================

    def next_token(self) -> str:
        while not self.reaches_end():
            if self.__meet_token != '':
                token = self.__meet_token
                self.__meet_token = ''
                self.offset(len(token))
                if token not in self.__space_tokens:
                    break
                else:
                    self.yield_str()
                    continue
            elif self.__in_wrapper:
                expect_close = self.__wrappers[self.__wrapper_index][1]
                if not self.offset_until(expect_close):
                    break
                if not self.__check_escape_symbol():
                    self.__in_wrapper = False
                    self.__meet_token = expect_close
                    break
            else:
                self.__meet_token = self.__check_meet_token()
                if self.__meet_token != '':
                    break
            self.offset(1)
        return self.next_token() if self.yield_len() == 0 and not self.reaches_end() else self.yield_str()

    # ========================================== Text processing ==========================================

    def source_len(self) -> int:
        return len(self.__text)

    def reaches_end(self, offset: int = 0) -> bool:
        return self.__parse_idx + offset >= self.source_len()

    def peek(self, offset: int = 0, count: int = 1) -> str:
        peek_index = self.__parse_idx + offset
        if peek_index < 0 or peek_index >= self.source_len():
            return ''
        return self.__text[peek_index : peek_index + count]

    def offset(self, offset):
        self.__parse_idx += offset
        if self.__parse_idx < 0:
            self.__parse_idx = 0
        elif self.__parse_idx > self.source_len():
            self.__parse_idx = self.source_len()

    def matches(self, text: str) -> bool:
        return self.peek(0, len(text)) == text

    def offset_until(self, text: str) -> bool:
        text_len = len(text)
        while not self.reaches_end(text_len):
            if self.matches(text):
                return True
            self.offset(1)
        return False

    def yield_len(self) -> int:
        return self.__parse_idx - self.__mark_idx

    def yield_str(self) -> str:
        slice_str = self.__text[self.__mark_idx: self.__parse_idx]
        self.__mark_idx = self.__parse_idx
        return slice_str

    # ========================================== Sub Check ==========================================

    def __check_meet_token(self) -> str:
        c = self.peek()
        for token in self.__tokens:
            if c == token[0] and self.matches(token):
                self.__wrapper_index = 0
                self.__in_wrapper = False
                for wrapper in self.__wrappers:
                    if token == wrapper[0]:
                        self.__in_wrapper = True
                        break
                    self.__wrapper_index += 1
                return token
        return ''

    def __check_escape_symbol(self) -> bool:
        for symbol in self.__escape_symbols:
            if self.peek(-len(symbol), len(symbol)) == symbol:
                return True
        return False


# ---------------------------------------------------- Token Parser ----------------------------------------------------

LABEL_TAG_TOKENS = [':', ',', '#', '"""', '\n', ' ']
LABEL_TAG_WRAPPERS = [('"""', '"""'), ('#', '\n')]
LABEL_TAG_ESCAPES_SYMBOLS = []


class LabelTagParser(TokenParser):
    def __init__(self):
        self.__last_tags = []
        self.__label_tags = []

    def get_label_tags(self) -> list:
        return self.__label_tags

    def parse(self, text: str) -> bool:
        parser = TokenParser()
        parser.config(LABEL_TAG_TOKENS, LABEL_TAG_WRAPPERS, LABEL_TAG_ESCAPES_SYMBOLS)
        parser.reset()
        parser.attach(text)

        ret = True
        until = ''
        expect = []
        next_step = 'label'

        while not parser.reaches_end():
            token = parser.next_token()

            print('-> Read token: ' + token)

            if until != '':
                if token == until:
                    until = ''
                continue
            elif len(expect) > 0:
                if token not in expect:
                    ret = False
                    print('Expect token: ' + str(expect) + ' but met: ' + token)
                expect = []

            if token == '#':
                until = '\n'
            elif token in [':', ',', '"""']:
                print('Drop token: ' + token)

            elif token == '\n':
                next_step = 'label'
            elif next_step == 'label':
                expect = [':']
                next_step = 'tag'
                self.switch_label(token)
            elif next_step == 'tag':
                expect = [',', '\n', '"""']
                self.append_tag(token)
            else:
                print('Should not reach here.')
        return ret

    def switch_label(self, label: str):
        self.__last_tags = []
        self.__label_tags.append((label, self.__last_tags))

    def append_tag(self, tag: str):
        if self.__last_tags is not None and tag not in self.__last_tags:
            self.__last_tags.append(tag)

    @staticmethod
    def label_tags_to_text(label: str, tags, whole: bool = False):
        if label is None or len(label) == 0:
            return ''
        if whole:
            if len(str(tags)) == 0:
                return ''
            tag_text = '"""' + str(tags) + '"""'
        else:
            tag_text = LabelTagParser.tags_to_text(tags)
            if len(tag_text) == 0:
                return ''
        return label + ': ' + tag_text + '\n'

    @staticmethod
    def tags_to_text(tags):
        if tags is None:
            return ''
        if isinstance(tags, (list, tuple)):
            tags = [str(tag) for tag in tags]
            if len(tags) > 0:
                text = ', '.join(tags)
            else:
                return ''
        else:
            text = str(tags)
        return text

    @staticmethod
    def text_to_tags(text):
        tags = text.split(',')


# --------------------------------------------------- class history ----------------------------------------------------

class History:

    # ----------------------------------------------------  Event  -----------------------------------------------------

    class Event:
        # Five key labels of an event: time, location, people, organization, event
        # Optional common labels: title, brief, uuid, author, tags, 成语

        def __init__(self, source: str = ''):
            self.__uuid = str(uuid.uuid4())
            self.__time = []
            self.__title = ''
            self.__brief = ''
            self.__event = ''
            self.__label_tags = {}
            self.__event_source = source

        # -------------------------------------------

        def reset(self):
            self.__time = []
            self.__title = ''
            self.__brief = ''
            self.__event = ''
            self.__label_tags = {}

        def set_source(self, source: str):
            self.__event_source = source

        def set_label_tags(self, label: str, tags: str or [str]):
            if label == 'uuid':
                self.__uuid = tags[0] if len(tags) > 0 else self.__uuid
            elif label == 'time':
                self.__time = tags
            elif label == 'title':
                self.__title = History.Event.__normalize_content_tags(tags)
            elif label == 'brief':
                self.__brief = History.Event.__normalize_content_tags(tags)
            elif label == 'event':
                self.__event = History.Event.__normalize_content_tags(tags)
            else:
                if label not in self.__label_tags.keys():
                    self.__label_tags[label] = tags
                else:
                    self.__label_tags[label].extend(tags)
                self.__label_tags[label] = list_unique(self.__label_tags[label])

        @staticmethod
        def __normalize_content_tags(tags: [str]) -> str:
            if isinstance(tags, str):
                return tags
            elif isinstance(tags, (list, tuple)):
                return ', '.join(tags)
            else:
                return str(tags)

        # -------------------------------------------

        def uuid(self) -> str:
            return self.__uuid

        def time(self) -> [float]:
            return self.__time

        def since(self) -> float:
            return min(self.__time)

        def until(self) -> float:
            return max(self.__time)

        def title(self) -> str:
            return self.__title

        def brief(self) -> str:
            return self.__brief

        def event(self) -> str:
            return self.__event

        def source(self) -> str:
            return self.__event_source

        # -------------------------------------------

        def tags(self, label: str):
            return self.__label_tags.get(label, [])

        def labels(self) -> [str]:
            return list(self.__label_tags.keys())

        def people(self) -> list:
            return self.tags('people')

        def location(self) -> list:
            return self.tags('location')

        def organization(self) -> list:
            return self.tags('organization')

        # -------------------------------------------

        def dump(self) -> str:
            text = '[START]:event\n'

            if self.__uuid is None or self.__uuid == '':
                self.__uuid = uuid.uuid1()

            text += LabelTagParser.label_tags_to_text('uuid', self.__uuid)
            text += LabelTagParser.label_tags_to_text('time', self.__time)
            text += '\n'

            for label in sorted(list(self.__label_tags.keys())):
                text += LabelTagParser.label_tags_to_text(label, self.__label_tags[label])
            text += '\n'

            text += LabelTagParser.label_tags_to_text('title', self.__title, True)
            text += LabelTagParser.label_tags_to_text('brief', self.__brief, True)
            text += LabelTagParser.label_tags_to_text('event', self.__event, True)

            return text

        def adapt(self, **argv) -> bool:
            if not check_condition_range(argv, 'time', self.__time):
                return False
            if 'contains' in argv.keys():
                looking_for = argv['contains']
                if self.__title.find(looking_for) == -1 and \
                   self.__brief.find(looking_for) == -1 and \
                   self.__event.find(looking_for) == -1:
                    return False
            if not self.__check_label_tags(argv):
                return False
            return True

        def __check_label_tags(self, expected: dict) -> bool:
            for key in expected:
                if key in ['time', 'title', 'brief', 'contains']:
                    continue
                if key not in self.__label_tags.keys():
                    return False
                expected_tags = expected.get(key)
                history_event_tags = self.__label_tags.get(key)
                if isinstance(expected_tags, (list, tuple)):
                    return compare_intersection(expected_tags, history_event_tags)
                else:
                    return expected_tags in history_event_tags
            return True

        # ----------------------------------- print -----------------------------------

        def __str__(self):
            return '---------------------------------------------------------------------------' + '\n' + \
                    '|UUID   : ' + str(self.__uuid) + '\n' + \
                    '|TIME   : ' + str(self.__time) + '\n' + \
                    '|LTAGS  : ' + str(self.__label_tags) + '\n' + \
                    '|TITLE  : ' + str(self.__title) + '\n' + \
                    '|BRIEF  : ' + str(self.__brief) + '\n' + \
                    '|EVENT  : ' + str(self.__event) + '\n' + \
                    '|SOURCE : ' + str(self.__event_source) + '\n' + \
                    '---------------------------------------------------------------------------'

    # -------------------------------------------------  Events Loader -------------------------------------------------

    class Loader:
        def __init__(self):
            self.__events = []

        def restore(self):
            self.__events.clear()

        def get_loaded_events(self) -> list:
            return self.__events

        def get_local_depot_path(self, depot: str) -> str:
            root_path = path.dirname(path.abspath(__file__))
            depot_path = path.join(root_path, 'depot', depot)
            return depot_path

        # events: History.Event or [History.Event]
        def to_local_depot(self, events, depot: str, file: str) -> bool:
            if not isinstance(events, (list, tuple)):
                events = [events]
            depot_path = self.get_local_depot_path(depot)
            file_path = path.join(depot_path, file)
            try:
                with open(file_path, 'wt', encoding='utf-8') as f:
                    for event in events:
                        event.set_source(file_path)
                        text = event.dump()
                        f.write(text)
                return True
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                return False
            finally:
                pass

        def from_local_depot(self, depot: str) -> int:
            try:
                depot_path = self.get_local_depot_path(depot)
                return self.from_directory(depot_path)
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                return 0
            finally:
                pass

        def from_directory(self, directory: str) -> int:
            try:
                files = self.enumerate_local_path(directory)
                return self.from_files(files)
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                return 0
            finally:
                pass

        def from_files(self, files: [str]):
            count = 0
            for file in files:
                if self.from_file(file):
                    count += 1
            return count

        def from_file(self, file: str) -> bool:
            try:
                with open(file, 'rt', encoding='utf-8') as f:
                    self.from_text(f.read(), file)
                return True
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                return False
            finally:
                pass

        def from_text(self, text: str, source: str = ''):
            error_list = []

            parser = LabelTagParser()
            parser.parse(text)

            section = ''
            event = None
            label_tags = parser.get_label_tags()

            for label, tags in label_tags:
                if label == '[START]':
                    self.yield_section(section, event)
                    event = None
                    if len(tags) == 0:
                        error_list.append('Missing start section.')
                    else:
                        section = 'tags[0]'
                    continue

                if event is None:
                    event = History.Event(source)
                event.set_label_tags(label, tags)

                if section != '' and label == section:
                    self.yield_section(section, event)
                    event = None

            self.yield_section(section, event)

        def yield_section(self, section, event):
            # TODO: different section, different class
            if event is not None:
                self.__events.append(event)

        def enumerate_local_path(self, root_path: str, suffix: [str] = None) -> list:
            files = []
            for parent, dirnames, filenames in os.walk(root_path):
                for filename in filenames:
                    if suffix is None:
                        files.append(path.join(parent, filename))
                    else:
                        for sfx in suffix:
                            if filename.endswith(sfx):
                                files.append(filename)
                                break
            return files

    # ---------------------------------------------------- History -----------------------------------------------------

    def __init__(self):
        self.__events = []
        self.__indexes = []

    def attach(self, loader):
        self.__events = loader.get_loaded_events()

    def print_events(self):
        for event in self.__events:
            print(event)


# ----------------------------------------------------------------------------------------------------------------------

def test_token_parser(text: str, expects: [str], tokens: list, wrappers: list, escape_symbols: list):
    parser = TokenParser()
    parser.config(tokens, wrappers, escape_symbols)
    parser.reset()
    parser.attach(text)
    for expect in expects:
        token = parser.next_token()
        assert token == expect


def test_token_parser_case_normal():
    text = '''
    line1:abc            # text in: comments
    line2
    line3:"""text in :wrapper"""
    '''
    expects = [
        '\n',
        'line1',
        ':',
        'abc',
        '#',
        ' text in: comments',
        '\n',
        'line2',
        '\n',
        'line3',
        ':',
        '"""',
        'text in :wrapper',
        '"""',
        '\n',
        ''
    ]
    test_token_parser(text, expects, LABEL_TAG_TOKENS, LABEL_TAG_WRAPPERS, LABEL_TAG_ESCAPES_SYMBOLS)


def test_token_parser_case_escape_symbol():
    pass


def test_history_basic():
    loader = History.Loader()
    count = loader.from_local_depot('example')

    print('Load successful: ' + str(count))

    history = History()
    history.attach(loader)

    history.print_events()


def main():
    # test_token_parser_case_normal()
    # test_token_parser_case_escape_symbol()
    test_history_basic()
    print('All test passed.')


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










