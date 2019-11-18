import os
import re
import math
import uuid
import ntpath
from functools import total_ordering

import requests
import traceback
import posixpath
from os import sys, path, listdir


# ----------------------------------------------------------------------------------------------------------------------

def str_to_int(text: str, default: int=0):
    try:
        return int(text)
    except Exception as e:
        return default
    finally:
        pass


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


# -------------------------------------------------- CN Time to Digit --------------------------------------------------

CN_NUM = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,

    '〇': 0,
    '一': 1,
    '二': 2,
    '三': 3,
    '四': 4,
    '五': 5,
    '六': 6,
    '七': 7,
    '八': 8,
    '九': 9,

    '零': 0,
    '壹': 1,
    '贰': 2,
    '叁': 3,
    '肆': 4,
    '伍': 5,
    '陆': 6,
    '柒': 7,
    '捌': 8,
    '玖': 9,

    '貮': 2,
    '两': 2,
}
CN_UNIT_L1 = {
    '十': 10,
    '拾': 10,
    '百': 100,
    '佰': 100,
    '千': 1000,
    '仟': 1000,
}
CN_UNIT_L2 = {
    '万': 10000,
    '萬': 10000,
    '亿': 100000000,
    '億': 100000000,
    '兆': 1000000000000,
}


def cn_num_to_digit(cn_num: str):
    """
    Algorithm:
        a.  The best way is parse from lower digit to upper digit.
        b.  The Chinese number has 2 level of unit:
                L1: 十百千; L2: 万亿兆...
            For L1 unit, it cannot be decorated. For L2 unit, it can be decorated by the unit that less than itself.
                Example: 一千万 is OK, but 一百千 or 一亿万 is invalid.
                More complex Example: 五万四千三百二十一万亿 四千三百二十一万 四千三百二十一
            We can figured out that:
                1. The L1 unit should not composite. 四千三百二十一 -> 4 * 1000 + 3 * 100 + 2 * 10 + 1
                2. The L2 unit should be composted. If we meet 万, the base unit should multiple with 10000.
                3. If we meet a larger L2 unit. The base unit should reset to it.
    :param cn_num: A single cn number string.
    :return: The digit that comes from cn number.
    """
    sum_num = 0
    unit_l1 = 1
    unit_l2 = 1
    unit_l2_max = 0
    digit_missing = False
    num_chars = list(cn_num)

    while num_chars:
        num_char = num_chars.pop()
        if num_char in CN_UNIT_L1:
            unit_l1 = CN_UNIT_L1.get(num_char)
            digit_missing = True
        elif num_char in CN_UNIT_L2:
            unit = CN_UNIT_L2.get(num_char)
            if unit > unit_l2_max:
                unit_l2_max = unit
                unit_l2 = unit
            else:
                unit_l2 *= unit
            unit_l1 = 1
            digit_missing = True
        elif num_char in CN_NUM:
            digit = CN_NUM.get(num_char) * unit_l1 * unit_l2
            # For discrete digit. It has no effect to the standard expression.
            unit_l1 *= 10
            sum_num += digit
            digit_missing = False
        else:
            continue
    if digit_missing:
        sum_num += unit_l1 * unit_l2

    print(cn_num + ' -> ' + str(sum_num))
    return sum_num


pattern = re.compile(r'([0123456789〇一二三四五六七八九零壹贰叁肆伍陆柒捌玖貮两十拾百佰千仟万萬亿億兆]+)')


def text_cn_num_to_arab(text: str) -> str:
    match_text = pattern.findall(text)
    match_text = list(set(match_text))
    match_text.sort(key=lambda x: len(x), reverse=True)
    for cn_num in match_text:
        text = text.replace(cn_num, str(cn_num_to_digit(cn_num)))
    return text


# ---------------------------------------------------- HistoryTime ----------------------------------------------------

# TODO: Use NLP to process nature language

class HistoryTime:

    TICK = int
    TICK_SEC = 1
    TICK_MIN = TICK_SEC * 60
    TICK_HOUR = TICK_MIN * 60
    TICK_DAY = TICK_HOUR * 24
    TICK_YEAR = TICK_DAY * 366
    TICK_WEEK = TICK(TICK_YEAR / 52)
    TICK_MONTH = [31, 60, 91, 121, 152, 182, 213, 244, 274, 304, 335, 366]

    EFFECTIVE_TIME_DIGIT = 6

    YEAR_FINDER = re.compile(r'(\d+年)')
    MONTH_FINDER = re.compile(r'(\d+月)')
    DAY_FINDER = re.compile(r'(\d+日)')

    # ------------------------------------------------------------------------

    SEPARATOR = [
        ',',
        '~',
        '～',
        '-',
        '－',
        '—',
        '―',
    ]

    SPACE_CHAR = [
        '约',
    ]

    REPLACE_CHAR = [
        ('元月', '1月'),
        ('正月', '1月'),
        ('世纪', '00'),
    ]

    PREFIX_CE = [
        'ac',
        'ce',
        'common era',
        '公元',
    ]

    PREFIX_BCE = [
        'bc',
        'bce',
        'before common era',
        '公元前',
        '前',
        '距今',
        '史前',
    ]

    def __init__(self):
        print("Create HistoryTime instance is not necessary.")

    # ------------------------------- Constant -------------------------------

    @staticmethod
    def year(year: int = 1) -> TICK:
        return year * HistoryTime.TICK_YEAR

    @staticmethod
    def month(month: int = 1) -> TICK:
        month = max(month, 1)
        month = min(month, 12)
        return HistoryTime.TICK_MONTH[month - 1]

    @staticmethod
    def week(week: int = 1) -> TICK:
        return int(week * HistoryTime.TICK_WEEK)

    @staticmethod
    def day(day: int = 1) -> TICK:
        return int(day * HistoryTime.TICK_DAY)

    # ------------------------------- Convert -------------------------------

    @staticmethod
    def year_of_tick(tick: TICK) -> int:
        return HistoryTime.date_of_tick(tick)[0]

    @staticmethod
    def month_of_tick(tick: TICK) -> int:
        return HistoryTime.date_of_tick(tick)[1]

    @staticmethod
    def day_of_tick(tick: TICK) -> int:
        return HistoryTime.date_of_tick(tick)[2]

    @staticmethod
    def date_of_tick(tick: TICK) -> (int, int, int):
        sign = 1 if tick >= 0 else -1
        day = 0
        year = sign * int(abs(tick) / HistoryTime.TICK_YEAR)
        month = 12
        year_mod = abs(tick) % HistoryTime.TICK_YEAR
        for i in range(0, len(HistoryTime.TICK_MONTH)):
            if year_mod <= HistoryTime.TICK_MONTH[i]:
                day = year_mod if i == 0 else year_mod - HistoryTime.TICK_MONTH[i - 1]
                month = i + 1
                break
        return year, month, day

    @staticmethod
    def decimal_year_to_tick(year: float) -> TICK:
        return int(year * HistoryTime.TICK_YEAR)

    @staticmethod
    def tick_to_decimal_year(tick: TICK) -> float:
        return HistoryTime.round_decimal_year(float(tick) / HistoryTime.TICK_YEAR)

    @staticmethod
    def tick_to_standard_string(tick: TICK) -> str:
        year, month, day = HistoryTime.date_of_tick(tick)
        if year < 0:
            text = str(-year) + ' BCE'
        else:
            text = str(year) + ' CE'
        text += '/' + str(month) + '/' + str(day)
        return text

    # ------------------------------- Calculation -------------------------------

    @staticmethod
    def round_decimal_year(year: float):
        return round(year, HistoryTime.EFFECTIVE_TIME_DIGIT)

    @staticmethod
    def decimal_year_equal(digital1: float, digital2: float):
        return abs(digital1 - digital2) < pow(1.0, -(HistoryTime.EFFECTIVE_TIME_DIGIT + 1))

    @staticmethod
    def build_history_time_tick(year: int = 0, month: int = 0, day: int = 0,
                                hour: int = 0, minute: int = 0, second: int = 0,
                                week: int = 0) -> TICK:
        sign = 1 if year >= 0 else -1
        tick = HistoryTime.year(abs(year)) + HistoryTime.month(month) + HistoryTime.day(day) + \
            hour * HistoryTime.TICK_HOUR + minute * HistoryTime.TICK_MIN + second * HistoryTime.TICK_MIN + \
            week * HistoryTime.TICK_WEEK
        return sign * tick

    # ------------------------------------------------------------------------

    @staticmethod
    def __get_first_item_except(items: list, expect: str):
        return items[0].replace(expect, '') if len(items) > 0 else ''

    @staticmethod
    def time_str_to_history_time(time_str: str) -> TICK:
        if time_str.lower().startswith(tuple(HistoryTime.PREFIX_BCE)):
            sign = -1
        elif time_str.lower().startswith(tuple(HistoryTime.PREFIX_CE)):
            sign = 1
        else:
            sign = 1
        arablized_str = text_cn_num_to_arab(time_str)
        day = HistoryTime.__get_first_item_except(HistoryTime.DAY_FINDER.findall(arablized_str), '日')
        year = HistoryTime.__get_first_item_except(HistoryTime.YEAR_FINDER.findall(arablized_str), '年')
        month = HistoryTime.__get_first_item_except(HistoryTime.MONTH_FINDER.findall(arablized_str), '月')

        if year == '':
            number_str = int("".join(filter(str.isdigit, arablized_str)))
            return HistoryTime.build_history_time_tick(sign * int(number_str))
        else:
            return HistoryTime.build_history_time_tick(sign * str_to_int(year), str_to_int(month), str_to_int(day))

    @staticmethod
    def time_text_to_history_times(text: str) -> [TICK]:
        time_text_list = HistoryTime.split_normalize_time_text(text)
        return [HistoryTime.time_str_to_history_time(time_text) for time_text in time_text_list]

    @staticmethod
    def split_normalize_time_text(text: str) -> [str]:
        unified_time_str = text
        for space in HistoryTime.SPACE_CHAR:
            unified_time_str = unified_time_str.replace(space, '')

        for old_char, new_char in HistoryTime.REPLACE_CHAR:
            unified_time_str = unified_time_str.replace(old_char, new_char)

        for i in range(1, len(HistoryTime.SEPARATOR)):
            unified_time_str = unified_time_str.replace(HistoryTime.SEPARATOR[i], HistoryTime.SEPARATOR[0])
        return unified_time_str.split(HistoryTime.SEPARATOR[0])

    # ------------------------------------------------------------------------

    @staticmethod
    def standardize(time_str: str) -> ([float], [str]):
        unified_time_str = time_str

        for space in HistoryTime.SPACE_CHAR:
            unified_time_str = unified_time_str.replace(space, '')

        for old_char, new_char in HistoryTime.REPLACE_CHAR:
            unified_time_str = unified_time_str.replace(old_char, new_char)

        for i in range(1, len(HistoryTime.SEPARATOR)):
            unified_time_str = unified_time_str.replace(HistoryTime.SEPARATOR[i], HistoryTime.SEPARATOR[0])

        time_list = []
        error_list = []
        sub_time_str_list = unified_time_str.split(HistoryTime.SEPARATOR[0])
        for sub_time_str in sub_time_str_list:
            try:
                num = HistoryTime.parse_single_time_str(sub_time_str.strip())
                time_list.append(num)
            except Exception as e:
                error_list.append(sub_time_str)
                print('Parse time error: ' + sub_time_str + ' -> ' + str(e))
            finally:
                pass
        return time_list, error_list

    @staticmethod
    def parse_single_time_str(time_str: str) -> float:
        if time_str.lower().startswith(tuple(HistoryTime.PREFIX_BCE)):
            sign = -1
        elif time_str.lower().startswith(tuple(HistoryTime.PREFIX_CE)):
            sign = 1
        else:
            sign = 1
        # non_numeric_chars = ''.join(set(string.printable) - set(string.digits))
        if '年' in time_str:
            time_str = time_str[0: time_str.find('年')]
        number_str = int("".join(filter(str.isdigit, time_str)))
        # number_str = time_str.translate(non_numeric_chars)
        return sign * float(number_str)

    @staticmethod
    def standard_time_to_str(std_time: float) -> str:
        year = math.floor(std_time)
        date = std_time - year
        text = str(year)
        if std_time < 0:
            text = str(-year) + ' BCE'
        else:
            text = str(year) + ' CE'
        return text


# ---------------------------------------------------- Token Parser ----------------------------------------------------

class TokenParser:
    def __init__(self):
        self.__text = ''
        self.__tokens = []
        self.__wrappers = []                  # [(start, close)]
        self.__space_tokens = [' ']
        self.__escape_symbols = ['\\']

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
                print('! Error wrapper format. Its format should be: [(start, close)], ...')
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
        return self.yield_str() if self.yield_len() > 0 or self.reaches_end() else self.next_token()

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

LABEL_TAG_TOKENS = [':', ',', ';', '#', '"""', '\n', ' ']
LABEL_TAG_WRAPPERS = [('"""', '"""'), ('#', '\n')]
LABEL_TAG_ESCAPES_SYMBOLS = ['\\']


class LabelTagParser:
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
                    print('! Expect token: ' + str(expect) + ' but met: ' + token)
                expect = []

            if token == '#':
                until = '\n'
            elif token in [':', ',', '"""']:
                print('Drop token: ' + token)

            elif token == '\n' or token == ';':
                next_step = 'label'
            elif next_step == 'label':
                expect = [':', ';']
                next_step = 'tag'
                self.switch_label(token)
            elif next_step == 'tag':
                expect = [',', '\n', '"""', ';']
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
    def label_tags_to_text(label: str, tags, new_line: str = '\n'):
        if label is None or len(label) == 0:
            return ''
        else:
            tag_text = LabelTagParser.tags_to_text(tags, True)
            if len(tag_text) == 0:
                return ''
        return label + ': ' + tag_text + new_line

    @staticmethod
    def tags_to_text(tags, persistence: bool = False):
        if tags is None:
            return ''
        if isinstance(tags, (list, tuple)):
            if persistence:
                tags = [LabelTagParser.check_wrap_tag(tag.strip()) for tag in tags]
            if len(tags) > 0:
                text = ', '.join(tags)
            else:
                return ''
        else:
            text = LabelTagParser.check_wrap_tag(tags)
        return text

    @staticmethod
    def check_wrap_tag(tag: any) -> str:
        if not isinstance(tag, str):
            tag = str(tag)
        tag = tag.replace('"""', '\\"""')
        # tag = tag.replace('\\', '\\\\')
        for token in LABEL_TAG_TOKENS:
            if token in tag:
                return '"""' + tag + '"""'
        return tag

    @staticmethod
    def label_tags_list_to_dict(label_tags_list: [str, [str]]) -> dict:
        label_tags_dict = {}
        for label, tags in label_tags_list:
            if label not in label_tags_list:
                label_tags_dict[label] = []
            label_tags_dict[label].extend(tags)
        return label_tags_dict


# --------------------------------------------------- class LabelTag ---------------------------------------------------

class LabelTag:
    def __init__(self):
        self.__label_tags = {}

    def reset(self):
        self.__label_tags.clear()

    def attach(self, label_tags_list: list):
        self.__label_tags = LabelTagParser.label_tags_list_to_dict(label_tags_list)

        # self.__label_tags.clear()
        # for label, tags in raw_label_tags:
        #     if label not in self.__label_tags:
        #         self.__label_tags[label] = []
        #     self.__label_tags[label].extend(tags)

    def get_tags(self, label: str) -> [str]:
        return self.__label_tags.get(label, [])

    def get_labels(self) -> [str]:
        return list(self.__label_tags.keys())

    def get_label_tags(self) -> dict:
        return self.__label_tags

    def is_label_empty(self, label: str) -> bool:
        tags = self.__label_tags.get(label)
        tags_text = LabelTagParser.tags_to_text(tags)
        return tags_text == ''

    def add_tags(self, label: str, tags: str or [str]):
        if not isinstance(tags, (list, tuple)):
            tags = [tags]
        if label not in self.__label_tags.keys():
            self.__label_tags[label] = tags
        else:
            self.__label_tags[label].extend(tags)
        self.__label_tags[label] = list_unique(self.__label_tags[label])

    def remove_label(self, label: str):
        if label in self.__label_tags.keys():
            del self.__label_tags[label]

    def dump_text(self, labels: [str] = None, compact: bool = False) -> str:
        text = ''
        new_line = '; ' if compact else '\n'
        if labels is None:
            labels = list(self.__label_tags.keys())
        for label in labels:
            tags = self.__label_tags.get(label)
            tags_text = LabelTagParser.tags_to_text(tags, True)
            if tags_text != '':
                text += label + ': ' + tags_text + new_line
        return text

    def filter(self,
               include_label_tags: dict, include_all: bool = True,
               exclude_label_tags: dict = None, exclude_any: bool = True) -> bool:
        if include_label_tags is not None and len(include_label_tags) > 0 and \
                not self.includes(include_label_tags, include_all):
            return False
        if exclude_label_tags is not None and len(exclude_label_tags) > 0 and \
                self.includes(exclude_label_tags, not exclude_any):
            return False
        return True

    def includes(self, label_tag_dict: dict, include_all: bool = False):
        result = False
        for key in label_tag_dict:
            if key not in self.__label_tags.keys():
                if include_all:
                    return False
                else:
                    continue
            expect_tags = label_tag_dict[key]
            exists_tags = self.__label_tags[key]
            for expect_tag in expect_tags:
                if expect_tag not in exists_tags:
                    if include_all:
                        return False
                else:
                    if include_all:
                        result = True
                    else:
                        return True
        return result

    # @staticmethod
    # def tags_to_text(tags: [str]) -> str:
    #     if tags is None:
    #         return ''
    #     elif isinstance(tags, str):
    #         return tags
    #     elif isinstance(tags, (list, tuple)):
    #         return ', '.join(tags)
    #     else:
    #         return str(tags)


# ----------------------------------------------- class HistoricalRecord -----------------------------------------------

class HistoricalRecord(LabelTag):
    # Five key labels of an record: time, location, people, organization, event
    # Optional common labels: title, brief, uuid, author, tags

    def __init__(self, source: str = ''):
        super(HistoricalRecord, self).__init__()
        self.__uuid = str(uuid.uuid4())
        self.__since = HistoryTime.TICK(0)
        self.__until = HistoryTime.TICK(0)
        self.__focus_label = ''
        self.__record_source = source

    # ------------------------------------------------------ Gets ------------------------------------------------------

    def uuid(self) -> str:
        return self.__uuid

    def since(self) -> HistoryTime.TICK:
        return self.__since

    def until(self) -> HistoryTime.TICK:
        return self.__until

    def source(self) -> str:
        return self.__record_source

    def get_focus_label(self) -> str:
        return self.__focus_label

    # -------------------------------------------

    def time(self) -> [str]:
        return self.get_tags('time')

    def people(self) -> list:
        return self.tags('people')

    def location(self) -> list:
        return self.tags('location')

    def organization(self) -> list:
        return self.tags('organization')

    def title(self) -> str:
        return self.get_tags('title')

    def brief(self) -> str:
        return self.get_tags('brief')

    def event(self) -> str:
        return self.get_tags('event')

    # ---------------------------------------------------- Features ----------------------------------------------------

    def reset(self):
        self.__focus_label = ''
        self.__record_source = ''
        super(HistoricalRecord, self).reset()

    def set_source(self, source: str):
        self.__record_source = source

    def set_focus_label(self, label: str):
        self.__focus_label = label

    def set_label_tags(self, label: str, tags: str or [str]):
        if isinstance(tags, str):
            tags = [tags]
        tags = [tag.strip() for tag in tags]

        if label == 'uuid':
            self.__uuid = str(tags[0])
        elif label == 'time':
            self.__try_parse_time_tags(tags)
            # if len(error_list) > 0:
            #     print('Warning: Cannot parse the time tag - ' + str(error_list))
        elif label == 'since':
            self.__since = HistoryTime.TICK(tags[0])
            return
        elif label == 'until':
            self.__until = HistoryTime.TICK(tags[0])
            return
        elif label == 'source':
            self.__record_source = str(tags[0])
            return
        super(HistoricalRecord, self).add_tags(label, tags)

    def to_index(self):
        record = HistoricalRecord()
        record.index_for(self)
        return record

    def index_for(self, his_record):
        self.reset()
        self.__focus_label = 'index'
        self.__uuid = his_record.uuid()
        self.__since = his_record.since()
        self.__until = his_record.until()
        self.__record_source = his_record.source()

        abstract = LabelTagParser.tags_to_text(his_record.title())
        abstract = LabelTagParser.tags_to_text(his_record.brief()) if abstract == '' else abstract
        abstract = LabelTagParser.tags_to_text(his_record.event()) if abstract == '' else abstract
        self.set_label_tags('abstract', abstract.strip()[:50])

    def period_adapt(self, since: HistoryTime.TICK, until: HistoryTime.TICK):
        return (since <= self.__since <= until) or (since <= self.__until <= until)

    @staticmethod
    def check_label_tags(self, label: str, tags: str or [str]) -> [str]:
        """
        Check label tags error.
        :param label:
        :param tags:
        :return: Error string list. The list is empty if there's no error occurs.
        """
        if label == 'time':
            time_list, error_list = HistoryTime.standardize(','.join(tags))
            return error_list
        else:
            return []

    def dump_record(self, compact: bool = False) -> str:
        new_line = '; ' if compact else '\n'
        dump_list = self.__get_sorted_labels()

        # Default focus label is 'event'
        if self.__focus_label is None or self.__focus_label == '':
            self.__focus_label = 'event'

        # Move the focus label to the tail.
        if self.__focus_label in dump_list:
            dump_list.remove(self.__focus_label)
        dump_list.append(self.__focus_label)

        # uuid should not in the common dump list
        if 'uuid' in dump_list:
            dump_list.remove('uuid')

        # Extra: The start label of HistoricalRecord
        text = LabelTagParser.label_tags_to_text('[START]', self.__focus_label, new_line)

        # Extra: The uuid of event
        if self.__uuid is None or self.__uuid == '':
            self.__uuid = str(uuid.uuid4())
        text += LabelTagParser.label_tags_to_text('uuid', self.__uuid, new_line)

        # ---------------------- Dump common labels ----------------------
        text += super(HistoricalRecord, self).dump_text(dump_list, compact)

        if self.__focus_label == 'index':
            text += LabelTagParser.label_tags_to_text('since', self.since(), new_line)
            text += LabelTagParser.label_tags_to_text('until', self.until(), new_line)
            text += LabelTagParser.label_tags_to_text('source', self.source(), new_line)

        # If the focus label missing, add it with 'end' tag
        if self.__focus_label not in dump_list or self.is_label_empty(self.__focus_label):
            # text += self.__focus_label + ': end' + new_line
            text += LabelTagParser.label_tags_to_text(self.__focus_label, 'end', new_line)

        return text

    #     if not check_condition_range(argv, 'time', self.__time):
    #         return False
    #     if 'contains' in argv.keys():
    #         looking_for = argv['contains']
    #         if self.__title.find(looking_for) == -1 and \
    #            self.__brief.find(looking_for) == -1 and \
    #            self.__event.find(looking_for) == -1:
    #             return False
    #     if not self.__check_label_tags(argv):
    #         return False
    #     return True
    #
    # def __check_label_tags(self, expected: dict) -> bool:
    #     for key in expected:
    #         if key in ['time', 'title', 'brief', 'contains']:
    #             continue
    #         if key not in self.__label_tags.keys():
    #             return False
    #         expected_tags = expected.get(key)
    #         history_event_tags = self.__label_tags.get(key)
    #         if isinstance(expected_tags, (list, tuple)):
    #             return compare_intersection(expected_tags, history_event_tags)
    #         else:
    #             return expected_tags in history_event_tags
    #     return True

    def __try_parse_time_tags(self, tags: [str]):
        his_times = HistoryTime.time_text_to_history_times(','.join(tags))
        if len(his_times) > 0:
            self.__since = min(his_times)
            self.__until = max(his_times)
        else:
            self.__since = HistoryTime.TICK(0)
            self.__until = HistoryTime.TICK(0)

        # time_list, error_list = HistoryTime.standardize(','.join(tags))
        # if len(time_list) > 0:
        #     self.__since = min(time_list)
        #     self.__until = max(time_list)
        # else:
        #     self.__since = 0.0
        #     self.__until = 0.0
        # return error_list

    def __get_sorted_labels(self) -> [str]:
        dump_list = []
        label_list = self.get_labels()

        # Sort the labels and put the focus label at the tail of list

        if 'time' in label_list:
            dump_list.append('time')
            label_list.remove('time')
        if 'people' in label_list:
            dump_list.append('people')
            label_list.remove('people')
        if 'location' in label_list:
            dump_list.append('location')
            label_list.remove('location')
        if 'organization' in label_list:
            dump_list.append('organization')
            label_list.remove('organization')

        dump_list.extend(sorted(label_list))

        if 'title' in dump_list:
            dump_list.remove('title')
            dump_list.append('title')
        if 'brief' in label_list:
            dump_list.remove('brief')
            dump_list.append('brief')
        if 'event' in label_list:
            dump_list.remove('event')
            dump_list.append('event')

        return dump_list

    # ----------------------------------------------------- print ------------------------------------------------------

    def __str__(self):
        return '---------------------------------------------------------------------------' + '\n' + \
                '|UUID   : ' + str(self.__uuid) + '\n' + \
                '|TIME   : ' + str(self.time()) + '\n' + \
                '|TITLE  : ' + str(self.title()) + '\n' + \
                '|BRIEF  : ' + str(self.brief()) + '\n' + \
                '|EVENT  : ' + str(self.event()) + '\n' + \
                '|SOURCE : ' + str(self.__record_source) + '\n' + \
                '---------------------------------------------------------------------------' \
               if self.__focus_label != 'index' else \
               '---------------------------------------------------------------------------' + '\n' + \
                '|UUID     : ' + str(self.uuid()) + '\n' + \
                '|SINCE    : ' + str(self.since()) + '\n' + \
                '|UNTIL    : ' + str(self.until()) + '\n' + \
                '|ABSTRACT : ' + str(self.get_tags('abstract')) + '\n' + \
                '|SOURCE   : ' + str(self.__record_source) + '\n' + \
                '---------------------------------------------------------------------------'


# --------------------------------------------------- class history ----------------------------------------------------

class HistoricalRecordLoader:
    def __init__(self):
        self.__records = []

    def restore(self):
        self.__records.clear()

    def get_loaded_records(self) -> list:
        return self.__records

    @staticmethod
    def to_local_depot(records: HistoricalRecord or [HistoricalRecord], depot: str, source: str) -> bool:
        base_name = os.path.basename(source)
        depot_path = HistoricalRecordLoader.join_local_depot_path(depot)
        source = path.join(depot_path, base_name)
        HistoricalRecordLoader.to_local_source(records, source)

    @staticmethod
    def to_local_source(records: HistoricalRecord or [HistoricalRecord], source: str):
        if not isinstance(records, (list, tuple)):
            records = [records]
        try:
            full_path = HistoricalRecordLoader.source_to_absolute_path(source)
            print('| <= Write record: ' + full_path)
            with open(full_path, 'wt', encoding='utf-8') as f:
                for record in records:
                    text = record.dump_record()
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
            depot_path = HistoricalRecordLoader.join_local_depot_path(depot)
            return self.from_directory(depot_path)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return 0
        finally:
            pass

    def from_directory(self, directory: str) -> int:
        try:
            files = HistoricalRecordLoader.enumerate_local_path(directory)
            return self.from_files(files)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return 0
        finally:
            pass

    def from_source(self, source: str) -> bool:
        if HistoricalRecordLoader.is_web_url(source):
            return self.from_web()
        else:
            return self.from_file(HistoricalRecordLoader.source_to_absolute_path(source))

    def from_files(self, files: [str]) -> int:
        count = 0
        for file in files:
            if self.from_file(file):
                count += 1
        return count

    def from_web(self, url: str) -> bool:
        try:
            r = requests.get(url)
            text = r.content.decode('utf-8')
            self.from_text(text)
            return True
        except Exception as e:
            print('Error when fetching from web: ' + str(e))
            return False
        finally:
            pass

    def from_file(self, file: str) -> bool:
        try:
            print('| => Load record: ' + file)
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

        focus = ''
        record = None
        label_tags = parser.get_label_tags()

        for label, tags in label_tags:
            if label == '[START]':
                self.yield_record(record)
                record = None
                focus = ''
                if len(tags) == 0:
                    error_list.append('Missing start section.')
                else:
                    focus = tags[0]
                continue

            if record is None:
                record = HistoricalRecord(HistoricalRecordLoader.normalize_source(source))
                record.set_focus_label(focus)
            record.set_label_tags(label, tags)

            if focus != '' and label == focus:
                self.yield_record(record)
                record = None
                focus = ''
        self.yield_record(record)

    def yield_record(self, record):
        if record is not None:
            self.__records.append(record)

    @staticmethod
    def is_web_url(_path: str):
        return _path.startswith('http') or _path.startswith('ftp')

    @staticmethod
    def is_absolute_path(_path: str):
        return ntpath.isabs(_path) or posixpath.isabs(_path)

    @staticmethod
    def source_to_absolute_path(source: str) -> str:
        return source if \
            HistoricalRecordLoader.is_absolute_path(source) else \
            path.join(HistoricalRecordLoader.get_local_depot_root(), source)

    @staticmethod
    def normalize_source(source: str) -> str:
        depot_root = HistoricalRecordLoader.get_local_depot_root()
        return source[len(depot_root) + 1:] if source.startswith(depot_root) else source

    @staticmethod
    def get_local_depot_root() -> str:
        project_root = path.dirname(path.abspath(__file__))
        depot_path = path.join(project_root, 'depot')
        return depot_path

    @staticmethod
    def join_local_depot_path(depot: str) -> str:
        root_path = HistoricalRecordLoader.get_local_depot_root()
        depot_path = path.join(root_path, depot)
        return depot_path

    @staticmethod
    def enumerate_local_path(root_path: str, suffix: [str] = None) -> list:
        files = []
        for parent, dirnames, filenames in os.walk(root_path):
            for filename in filenames:
                if suffix is None:
                    files.append(path.join(parent, filename))
                else:
                    for sfx in suffix:
                        if filename.endswith(sfx):
                            files.append(path.join(parent, filename))
                            break
        return files


# ------------------------------------------- class HistoricalRecordIndexer --------------------------------------------

class HistoricalRecordIndexer:
    def __init__(self):
        self.__indexes = []

    def restore(self):
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
        print('| => Write record: ' + file)
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


# --------------------------------------------------- class history ----------------------------------------------------

class History:
    def __init__(self):
        self.__records = []
        # Deprecated
        self.__indexes = []

    # ----------------------------------- Deprecated :Index -----------------------------------

    def set_indexes(self, indexes: [HistoricalRecord]):
        self.__indexes.clear()
        self.__indexes.extend(indexes)

    def get_indexes(self) ->[HistoricalRecord]:
        return self.__indexes

    # -------------------------------------- Gets / Sets --------------------------------------

    def add_record(self, record: HistoricalRecord) -> bool:
        if record is None or record.uuid() is None or record.uuid() == '':
            return False
        _uuid = record.uuid()
        exists_record = self.get_record_by_uuid(_uuid)
        if exists_record is not None:
            self.__records.remove(exists_record)
        self.__records.append(record)
        return True

    def remove_record(self, record: HistoricalRecord):
        if record in self.__records:
            self.__records.remove(record)

    def add_records(self, records: [HistoricalRecord]):
        for record in records:
            self.add_record(record)

    def remove_records(self, records: [HistoricalRecord]):
        for record in records:
            self.remove_record(record)

    def get_records(self) -> [HistoricalRecord]:
        return self.__records

    def attach_records(self, records: [HistoricalRecord]):
        self.__records.clear()
        self.__records.extend(records)

    def clear_records(self):
        self.__records.clear()

    # --------------------------------------- Updates ---------------------------------------

    def update_records(self, records: [HistoricalRecord]):
        History.upsert_records(self.__records, records)

    def update_indexes(self, indexes: [HistoricalRecord]):
        History.upsert_records(self.__indexes, indexes)

    # --------------------------------------- Select ---------------------------------------

    def get_record_by_uuid(self, _uuid: str) -> HistoricalRecord or None:
        for record in self.__records:
            if record.uuid() == _uuid:
                return record
        return None

    def get_record_by_source(self, source: str) -> HistoricalRecord or None:
        return [record for record in self.__records if record.source() == source]

    def select_records(self, _uuid: str or [str] = None,
                       sources: str or [str] = None, focus_label: str = '',
                       include_label_tags: dict = None, include_all: bool = True,
                       exclude_label_tags: dict = None, exclude_any: bool = True) ->[HistoricalRecord]:
        records = self.__records.copy()

        if _uuid is not None and len(_uuid) != 0:
            if not isinstance(_uuid, (list, tuple)):
                _uuid = [_uuid]
            records = [record for record in records if record.uuid() in _uuid]

        if sources is not None and len(sources) != 0:
            if not isinstance(sources, (list, tuple)):
                sources = [sources]
            records = [record for record in records if record.source() in sources]

        if focus_label is not None and focus_label != '':
            records = [record for record in records if record.get_focus_label() == focus_label]

        if include_label_tags is not None or exclude_label_tags is not None:
            records = [record for record in records if record.filter(include_label_tags, include_all,
                                                                     exclude_label_tags, exclude_any)]
        return records

    # ------------------------------------- Load -------------------------------------

    def load_source(self, source: str) -> [HistoricalRecord]:
        loader = HistoricalRecordLoader()
        result = loader.from_source(source)
        if result:
            self.add_records(loader.get_loaded_records())
        return loader.get_loaded_records() if result else []

    def load_depot(self, depot: str) -> bool:
        loader = HistoricalRecordLoader()
        result = loader.from_local_depot(depot)
        if result:
            self.add_records(loader.get_loaded_records())
        return result != 0

    def load_path(self, _path: str):
        loader = HistoricalRecordLoader()
        result = loader.from_directory(_path)
        if result:
            self.add_records(loader.get_loaded_records())
        return result != 0

    # ----------------------------------- Print -----------------------------------

    def print_records(self):
        for record in self.__records:
            print(record)

    def print_indexes(self):
        for index in self.__indexes:
            print(index)

    # ------------------------------- Static Methods -------------------------------

    @staticmethod
    def sort_records(records: [HistoricalRecord]) -> [HistoricalRecord]:
        return sorted(records, key=lambda x: x.since())

    @staticmethod
    def unique_records(records: [HistoricalRecord]) -> [HistoricalRecord]:
        return {r.uuid(): r for r in records}.values()

    @staticmethod
    def upsert_records(records_list: [HistoricalRecord], records_new: [HistoricalRecord]):
        new_records = {r.uuid(): r for r in records_new}
        for i in range(0, len(records_list)):
            _uuid = records_list[i].uuid()
            if _uuid in new_records.keys():
                records_list[i] = new_records[_uuid]
                del new_records[_uuid]
        records_list.extend(new_records.values())


# ----------------------------------------------------- Test Code ------------------------------------------------------

# --------------------------- Time Parser ------------------------------

def test_cn_time_to_digit():
    assert cn_num_to_digit('零') == 0
    assert cn_num_to_digit('一') == 1
    assert cn_num_to_digit('二') == 2
    assert cn_num_to_digit('两') == 2
    assert cn_num_to_digit('三') == 3
    assert cn_num_to_digit('四') == 4
    assert cn_num_to_digit('五') == 5
    assert cn_num_to_digit('六') == 6
    assert cn_num_to_digit('七') == 7
    assert cn_num_to_digit('八') == 8
    assert cn_num_to_digit('九') == 9

    assert cn_num_to_digit('十') == 10
    assert cn_num_to_digit('百') == 100
    assert cn_num_to_digit('千') == 1000
    assert cn_num_to_digit('万') == 10000
    assert cn_num_to_digit('亿') == 100000000

    assert cn_num_to_digit('一十') == 10
    assert cn_num_to_digit('一百') == 100
    assert cn_num_to_digit('一千') == 1000
    assert cn_num_to_digit('一万') == 10000
    assert cn_num_to_digit('一亿') == 100000000

    assert cn_num_to_digit('二十') == 20
    assert cn_num_to_digit('两百') == 200
    assert cn_num_to_digit('五千') == 5000
    assert cn_num_to_digit('八万') == 80000
    assert cn_num_to_digit('九亿') == 900000000

    assert cn_num_to_digit('十亿') == 1000000000
    assert cn_num_to_digit('百亿') == 10000000000
    assert cn_num_to_digit('千亿') == 100000000000
    assert cn_num_to_digit('万亿') == 1000000000000
    assert cn_num_to_digit('十万亿') == 10000000000000
    assert cn_num_to_digit('百万亿') == 100000000000000
    assert cn_num_to_digit('千万亿') == 1000000000000000
    assert cn_num_to_digit('万万亿') == 10000000000000000
    assert cn_num_to_digit('亿亿') == 10000000000000000

    assert cn_num_to_digit('一千一百一十一亿一千一百一十一万一千一百一十一') == 111111111111
    assert cn_num_to_digit('九千八百七十六亿五千四百三十二万一千两百三十四') == 987654321234
    assert cn_num_to_digit('五万四千三百二十一万亿四千三百二十一万四千三百二十一') == 54321000043214321
    assert cn_num_to_digit('九千八百七十六万一千二百三十四亿五千四百三十二万一千两百三十四') == 9876123454321234

    print(text_cn_num_to_arab('''
    基本数字有：一，二或两，三，四及五，六，七和八，以及九共十个数字
    支持的位数包括：最简单的十，大一点的百，还有千，更大的万和最终的亿共五个进位
    先来点简单的：
        一万
        二千
        三百
        八亿
    以及由此组合成的复杂数字：
        其中有五十二个
        或者是一百七十三只
        试我们试试两百零六怎样
        那么三千五百七十九呢
        一千两百二十亿零两万零五十肯定有问题
        再看看这个数字一千五百三十六万零四十
        这个够复杂了吧一万八千亿三千六百五十万零七十九
    以及离散数字
       二九九七九二四五八
       三点一四一五九二六
    '''))


# --------------------------- Time Parser ------------------------------

def __verify_year_month(time_str, year_expect, month_expect):
    times = HistoryTime.time_text_to_history_times(time_str)
    year, month, day = HistoryTime.date_of_tick(times[0])
    assert year == year_expect and month == month_expect


def test_history_time_year():
    __verify_year_month('9百年', 900, 1)
    __verify_year_month('2010年', 2010, 1)
    __verify_year_month('二千年', 2000, 1)
    __verify_year_month('公元3百年', 300, 1)
    __verify_year_month('公元三百年', 300, 1)
    __verify_year_month('一万亿年', 1000000000000, 1)

    __verify_year_month('公元前1900年', -1900, 1)
    __verify_year_month('公元前500年', -500, 1)
    __verify_year_month('前一百万年', -1000000, 1)
    __verify_year_month('前200万年', -2000000, 1)
    __verify_year_month('前一万亿年', -1000000000000, 1)


def test_history_time_year_month():
    __verify_year_month('1900年元月', 1900, 1)
    __verify_year_month('1900年正月', 1900, 1)

    __verify_year_month('1900年一月', 1900, 1)
    __verify_year_month('1900年二月', 1900, 2)
    __verify_year_month('1900年三月', 1900, 3)
    __verify_year_month('1900年四月', 1900, 4)
    __verify_year_month('1900年五月', 1900, 5)
    __verify_year_month('1900年六月', 1900, 6)
    __verify_year_month('1900年七月', 1900, 7)
    __verify_year_month('1900年八月', 1900, 8)
    __verify_year_month('1900年九月', 1900, 9)
    __verify_year_month('1900年十月', 1900, 10)
    __verify_year_month('1900年十一月', 1900, 11)
    __verify_year_month('1900年十二月', 1900, 12)

    # --------------------------------------------------

    __verify_year_month('公元前200年', -200, 1)

    __verify_year_month('公元前200年元月', -200, 1)
    __verify_year_month('公元前200年正月', -200, 1)

    __verify_year_month('公元前200年一月', -200, 1)
    __verify_year_month('公元前200年二月', -200, 2)
    __verify_year_month('公元前200年三月', -200, 3)
    __verify_year_month('公元前200年四月', -200, 4)
    __verify_year_month('公元前200年五月', -200, 5)
    __verify_year_month('公元前200年六月', -200, 6)
    __verify_year_month('公元前200年七月', -200, 7)
    __verify_year_month('公元前200年八月', -200, 8)
    __verify_year_month('公元前200年九月', -200, 9)
    __verify_year_month('公元前200年十月', -200, 10)
    __verify_year_month('公元前200年十一月', -200, 11)
    __verify_year_month('公元前200年十二月', -200, 12)


def test_time_text_to_history_times():
    times = HistoryTime.time_text_to_history_times('220 - 535')
    assert HistoryTime.year_of_tick(times[0]) == 220 and HistoryTime.year_of_tick(times[1]) == 535


# ---------------------------- Token & Parser ----------------------------

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


# -------------------------------- History --------------------------------

def test_history_basic():
    loader = HistoricalRecordLoader()
    count = loader.from_local_depot('example')

    print('Load successful: ' + str(count))

    history = History()
    records = loader.get_loaded_records()
    history.update_records(records)
    history.print_records()


def test_history_filter():
    loader = HistoricalRecordLoader()
    loader.from_local_depot('example')

    history = History()
    history.update_records(loader.get_loaded_records())

    records = history.select_records(include_label_tags={'tags': ['tag1']},
                                     include_all=True)
    assert len(records) == 1

    records = history.select_records(include_label_tags={'tags': ['tag3']},
                                     include_all=True)
    assert len(records) == 3

    records = history.select_records(include_label_tags={'tags': ['tag5', 'odd']},
                                     include_all=True)
    assert len(records) == 3

    records = history.select_records(include_label_tags={'tags': ['tag1', 'even']},
                                     include_all=False)
    assert len(records) == 3

    records = history.select_records(include_label_tags={'tags': ['tag']},
                                     include_all=True)
    assert len(records) == 0

    records = history.select_records(include_label_tags={'author': ['Sleepy']},
                                     include_all=True)
    assert len(records) == 4


# -------------------------------- Indexer --------------------------------

def test_generate_index():
    depot_path = HistoricalRecordLoader.join_local_depot_path('China')
    indexer = HistoricalRecordIndexer()
    indexer.index_path(depot_path)
    indexer.dump_to_file('test_history.index')


def test_load_index():
    indexer = HistoricalRecordIndexer()
    indexer.load_from_file('test_history.index')
    history = History()
    history.update_indexes(indexer.get_indexes())
    history.print_indexes()


def test_history_time_basic():
    HistoryTime.year()


# ----------------------------------------------------- File Entry -----------------------------------------------------

def main():
    test_history_time_year()
    test_history_time_year_month()
    test_cn_time_to_digit()
    test_time_text_to_history_times()
    test_token_parser_case_normal()
    test_token_parser_case_escape_symbol()
    test_history_basic()
    test_history_filter()
    test_generate_index()
    test_load_index()
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










