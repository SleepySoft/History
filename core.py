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
                expect = [',', '\n']
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


# --------------------------------------------------- class history ----------------------------------------------------

class History:

    class Event:
        # Five key labels of an event: time, location, people, organization, event
        # Optional common labels: title, brief, uuid, author, tags, 成语

        def __init__(self):
            self.__uuid = ''
            self.__time = []
            self.__title = ''
            self.__brief = ''
            self.__event = ''
            self.__label_tags = {}

        # -------------------------------------------

        def set_label_tags(self, label: str, tags: str):
            if label == 'uuid':
                self.__uuid = tags[0]
            elif label == 'time':
                self.__time = tags
            elif label == 'title':
                self.__title = tags
            elif label == 'brief':
                self.__brief = tags
            elif label == 'event':
                self.__event = tags
            else:
                if label not in self.__label_tags.keys():
                    self.__label_tags[label] = tags
                else:
                    self.__label_tags[label].extend(tags)
                self.__label_tags[label] = list_unique(self.__label_tags[label])

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

        # ---------------------------------------- print ---------------------------------------

        def __str__(self):
            return '********************************** Event **********************************' + '\n' + \
                    'UUID  : ' + str(self.__uuid) + '\n' + \
                    'TIME  : ' + str(self.__time) + '\n' + \
                    'LTAGS : ' + str(self.__label_tags) + '\n' + \
                    'TITLE : ' + str(self.__title) + '\n' + \
                    'BRIEF : ' + str(self.__brief) + '\n' + \
                    'EVENT : ' + str(self.__event) + '\n' + \
                    '***************************************************************************'

    def __init__(self):
        self.__events = []

    def load_local_depot(self, depot: str) -> int:
        try:
            root_path = path.dirname(path.abspath(__file__))
            depot_path = path.join(root_path, 'depot', depot)
            return self.load_directory(depot_path)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return 0
        finally:
            pass

    def load_directory(self, directory: str) -> int:
        try:
            ls = listdir(directory)
            ls = [path.join(directory, f) for f in ls]
            files = [f for f in ls if path.isfile(f)]

            count = 0
            for file in files:
                if self.load_file(file):
                    count += 1
            return count
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return 0
        finally:
            pass

    def load_file(self, file: str) -> bool:
        try:
            with open(file, 'rt', encoding='utf-8') as f:
                self.load_text(f.read())
            return True
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return False
        finally:
            pass

    def load_text(self, text: str):
        parser = LabelTagParser()
        parser.parse(text)

        event = None
        label_tags = parser.get_label_tags()

        for label, tags in label_tags:
            if label == 'time':
                if event is not None:
                    self.__events.append(event)
                event = History.Event()
            event.set_label_tags(label, tags)
        if event is not None:
            self.__events.append(event)

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
    history = History()
    count = history.load_local_depot('example')
    print(count)
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










