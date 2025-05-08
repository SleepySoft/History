"""
这个模块用来处理历史时间。
历史时间类型为TICK，单位为秒。以公元纪元开始时为零点。公元后为正，直至无穷；公元前为负，亦至无穷。
TICK是真实世界的时间刻度，而年月日是人为制定的历法。TICK和各种datetime格式并没有必然的对应关系。
公元前的月和日仅供参考，算法以公元前一日为公元前1年12月31日，公元前二日为公元前1年12月30日，以次类推。

这个模块实现以下功能：
    1. 将自然语言的时间表示转化为TICK。程序并未采用NLP而是使用了简单粗暴的方法，适用于历史文章中的时间表示方法
        a) 常见的表示方法如：“公元前200年”，“距今1000年前”，“xx年五月”等，不支持年号。
        b) 多个时间以“~”或“-”之类的分隔符分隔，例如“公元前200年 - 公元前300年”
        c) 不支持星期
        d) 同时支持标准时间日期格式：YYYY-mm-dd HH:MM:SS
"""

import re
import sys
import math
import datetime
import traceback
import typing
from typing import Tuple

try:
    from Utility.to_arab import *
    from Utility.history_public import *
except Exception as e:
    from os import path

    root_path = path.dirname(path.dirname(path.abspath(__file__)))
    sys.path.append(root_path)
    from Utility.to_arab import *
    from Utility.history_public import *
finally:
    pass

TICK = int
TICK_SEC = 1
TICK_MIN = TICK_SEC * 60  # 60
TICK_HOUR = TICK_MIN * 60  # 3600
TICK_DAY = TICK_HOUR * 24  # 86400
TICK_MONTH_AVG = TICK_DAY * 30  # 2592000
TICK_YEAR = TICK_DAY * 365  # 31536000
TICK_LEAP_YEAR = TICK_DAY * 366  # 31622400
TICK_WEEK = TICK(TICK_YEAR / 52)  # 608123.0769230769

MONTH_DAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MONTH_DAYS_LEAP_YEAR = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

MONTH_DAYS_SUM = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
MONTH_DAYS_SUM_LEAP_YEAR = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]

YEAR_DAYS = 365
YEAR_DAYS_LEAP_YEAR = 366

MONTH_SEC = [86400 * days for days in MONTH_DAYS_SUM]
MONTH_SEC_LEAP_YEAR = [86400 * days for days in MONTH_DAYS_SUM_LEAP_YEAR]

DAYS_PER_4_YEARS = 365 * 4 + 4 // 4 - 4 // 100 + 4 // 400
DAYS_PER_100_YEARS = 365 * 100 + 100 // 4 - 100 // 100 + 100 // 400
DAYS_PER_400_YEARS = 365 * 400 + 400 // 4 - 400 // 100 + 400 // 400

EFFECTIVE_TIME_DIGIT = 10

YEAR_FINDER = re.compile(r'(\d+?\s*年)')
MONTH_FINDER = re.compile(r'(\d+?\s*月)')
DAY_FINDER = re.compile(r'(\d+?\s*日)')

DEFAULT_YEAR_FORMAT = "%Y"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_TIME_FORMAT = "%H:%M:%S"
DEFAULT_DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# ------------------------------------------------------------------------

SEPARATOR = [
    ',',
    '，',
    '~',
    '～',
    '-',
    '–',
    '－',
    '—',
    '―',
    '─',
    '至',
    '到',
]

SPACE_CHAR = [
    '约',
]

REPLACE_CHAR = [
    ('元月', '1月'),
    ('正月', '1月'),
    ('世纪', '00'),
    ('至今', datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')),
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


# ------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------- Convert -----------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------

SUPPORT_DATE_TIME_STR_FORMAT = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%H:%M:%S', '%Y%m%d']


def now_tick() -> TICK:
    """
    Get now datetime in TICK
    :return: TICK
    """
    return datetime_to_tick(datetime.datetime.now())


def time_text_to_ticks(time_text: str):
    """
    *** All you need is this function ***

    Convert time text to TICK. The time string can contain multiple sub time string which split by SEPARATOR.
    Note that the text in '[]' will not be split. The standard datetime string has to be surrounded by '[]'.
    It will try to convert each sub string by standard datetime format first, then try to convert as natural language.
    :param time_text: Any time text
    :return: The list of TICK
    """
    time_ticks = []
    sub_time_texts = __split_natural_language_time_text(time_text)

    # print('------------------------------------------')
    for sub_time_text in sub_time_texts:
        # Try to convert to datetime
        dt = time_str_to_datetime(sub_time_text)
        if dt is not None:
            tick = datetime_to_tick(dt)
            # print(f'{sub_time_text} (datetime) -> {tick}')
        else:
            tick = __single_natural_language_time_to_tick(sub_time_text)
            # print(f'{sub_time_text} -> {tick}')
        if tick is not None:
            time_ticks.append(tick)
    # print('------------------------------------------')
    return time_ticks


def time_str_to_datetime(text: str) -> datetime.datetime | None:
    """
    Try to convert standard time format (only standard time format) to python datetime.
    Support format lists in SUPPORT_DATE_TIME_STR_FORMAT.
    Q: Why not use dateutil?
    A: Because the parse process is hard to control. We have to detect history date.
    :param text:The data time text.
    :return: Python datetime if text format is valid else None
    """
    if isinstance(text, datetime.datetime):
        return text
    for f in SUPPORT_DATE_TIME_STR_FORMAT:
        try:
            return datetime.datetime.strptime(text, f)
        except Exception:
            pass
        finally:
            pass
    return None


def format_tick(tick: TICK, show_date: bool = False, show_time: bool = False) -> str:
    """
    Format TICK to string. Default only format the year.
    :param tick:
    :param show_date:
    :param show_time:
    :return:
    """

    year, month, day, hour, minute, second = tick_to_date_time_data(tick)
    if year < 0:
        text = f'{-year}'
    else:
        text = str(year)
    if show_date:
        text += f'/{month}/{day}'
    if show_time:
        text += f'{hour:02d}:{minute:02d}:{second:02d}'
    return text


def format_datetime(dt: datetime.datetime, show_date: bool = True, show_time: bool = True):
    text = dt.strftime(DEFAULT_DATE_FORMAT) if show_date else dt.strftime(DEFAULT_DATE_FORMAT)
    if show_time:
        text += ' ' + dt.strftime(DEFAULT_TIME_FORMAT)
    return f'[{text}]' if show_date or show_time else text


def tick_to_datetime(tick: TICK) -> datetime.datetime | None:
    """
    Convert History TICK to python datetime. If the date time is out of the datetime range. Return None.
    :param tick: The History TICK
    :return: datetime or None if conversion has issue.
    """
    date_time = tick_to_date_time_data(tick)
    try:
        return datetime.datetime(*date_time)
    except Exception as e:
        print(e)
        return None
    finally:
        pass


def datetime_to_tick(dt: datetime.datetime) -> TICK:
    """
    Convert python time format to History TICK
    :param dt: datetime.
    :return: History TICK
    """
    return date_time_data_to_tick(*datetime_to_date_time_data(dt))


def datetime_to_date_time_data(dt: datetime.datetime) -> Tuple[int, int, int, int, int, int]:
    """
    Convert datetime to (year, month, day, hour, minute, second)
    """
    return dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second


# ------------------------------------------------------------------------------------------------------------------
# -------------------------------------------- Text Analysis and Parse ---------------------------------------------
# ------------------------------------------------------------------------------------------------------------------

def __split_natural_language_time_text(text: str) -> [str]:
    """
    Split multiple natural language time text in one sentence to single time text array.
    Note that the '[]' surrounding will be removed.
    :param text: The natural language time text
    :return: The list of single time text.
    """
    unified_time_str = text
    for space in SPACE_CHAR:
        unified_time_str = unified_time_str.replace(space, '')

    for old_char, new_char in REPLACE_CHAR:
        unified_time_str = unified_time_str.replace(old_char, new_char)

    # 匹配方括号“[]”包围的内容
    bracket_content = re.findall(r'\[.*?\]', unified_time_str)
    # 移除方括号“[]”包围的内容
    s = re.sub(r'\[.*?\]', '', unified_time_str)

    # 使用SEPARATOR列表中的分隔符进行分割
    for sep in SEPARATOR:
        s = s.replace(sep, SEPARATOR[0])

    time_str_list = bracket_content + s.split(SEPARATOR[0])
    time_str_list = list(filter(None, (time_str.strip('[]').strip() for time_str in time_str_list)))

    return time_str_list


def __get_first_item_except(items: list, expect: str):
    return items[0].replace(expect, '') if len(items) > 0 else ''


def __single_natural_language_time_to_tick(time_text: str) -> TICK | None:
    """
    Convert natural language time description to TICK.
    Note that this analysis process does not apply to datetime format strings.
    The best way should be using NLP.
    :param time_text: The time string
    :return: TICK
    """
    if str_includes(time_text.lower().strip(), PREFIX_BCE):
        sign = -1
    else:
        sign = 1

    arablized_str = text_cn_num_to_arab(time_text)
    day = __get_first_item_except(DAY_FINDER.findall(arablized_str), '日')
    year = __get_first_item_except(YEAR_FINDER.findall(arablized_str), '年')
    month = __get_first_item_except(MONTH_FINDER.findall(arablized_str), '月')

    if year == '':
        try:
            number_str = int("".join(filter(str.isdigit, arablized_str)))
            return date_time_data_to_tick(sign * int(number_str), 1, 1)
        except Exception as _:
            return None
    else:
        year = sign * str_to_int(year)
        month = str_to_int(month)
        day = str_to_int(day)

        year = 1 if year == 0 else year
        month = max(month, 1)
        month = min(month, 12)
        day = max(day, 1)
        day = min(day, month_days(month, is_leap_year(year)))

        return date_time_data_to_tick(year, month, day)


# def time_text_to_history_times(text: str) -> [TICK]:
#     time_text_list = __split_natural_language_time_text(text)
#     return [__single_natural_language_time_to_tick(time_text) for time_text in time_text_list]


# ------------------------------------------------------------------------

#
# def standardize(time_str: str) -> ([float], [str]):
#     unified_time_str = time_str
#
#     for space in SPACE_CHAR:
#         unified_time_str = unified_time_str.replace(space, '')
#
#     for old_char, new_char in REPLACE_CHAR:
#         unified_time_str = unified_time_str.replace(old_char, new_char)
#
#     for i in range(1, len(SEPARATOR)):
#         unified_time_str = unified_time_str.replace(SEPARATOR[i], SEPARATOR[0])
#
#     time_list = []
#     error_list = []
#     sub_time_str_list = unified_time_str.split(SEPARATOR[0])
#     for sub_time_str in sub_time_str_list:
#         try:
#             num = parse_single_time_str(sub_time_str.strip())
#             time_list.append(num)
#         except Exception as e:
#             error_list.append(sub_time_str)
#             print('Parse time error: ' + sub_time_str + ' -> ' + str(e))
#         finally:
#             pass
#     return time_list, error_list
#
#
# def parse_single_time_str(time_str: str) -> float:
#     if time_str.lower().startswith(tuple(PREFIX_BCE)):
#         sign = -1
#     elif time_str.lower().startswith(tuple(PREFIX_CE)):
#         sign = 1
#     else:
#         sign = 1
#     # non_numeric_chars = ''.join(set(string.printable) - set(string.digits))
#     if '年' in time_str:
#         time_str = time_str[0: time_str.find('年')]
#     number_str = int("".join(filter(str.isdigit, time_str)))
#     # number_str = time_str.translate(non_numeric_chars)
#     return sign * float(number_str)


# def standard_time_to_str(std_time: float) -> str:
#     year = math.floor(std_time)
#     date = std_time - year
#     text = str(year)
#     if std_time < 0:
#         text = str(-year) + ' BCE'
#     else:
#         text = str(year) + ' CE'
#     return text


# def tick_to_cn_date_text(his_tick: TICK) -> str:
#     year, month, day, _ = tick_to_date(his_tick)
#     if year < 0:
#         text = '公元前' + str(-year) + '年'
#     else:
#         text = '公元' + str(-year) + '年'
#     return text + str(month) + '月' + str(day) + '日'


# ------------------------------------------------------------------------------------------------------------------
# -------------------------------------------- Strict DateTime From AD ---------------------------------------------
# ------------------------------------------------------------------------------------------------------------------

# --------------------------------------- Constant ---------------------------------------


def year_ticks(leap_year: bool) -> TICK:
    """
    Get seconds of a year.
    :param leap_year: Is leap year or not
    :return: seconds of 365 days if leap year else seconds of 366 days
    """
    return TICK_LEAP_YEAR if leap_year else TICK_YEAR


def year_days(leap_year: bool) -> int:
    """
    Get days of a year.
    :param leap_year: Is leap year or not
    :return: 365 days if leap year else 366 days
    """
    return YEAR_DAYS_LEAP_YEAR if leap_year else YEAR_DAYS


def month_ticks(month: int, leap_year: bool) -> TICK:
    """
    Get seconds of the month.
    :param month: The month should be 0 <= month <= 13
    :param leap_year: Is leap year or not
    :return: The seconds of the month.
    """
    assert 0 <= month <= 13
    return MONTH_SEC_LEAP_YEAR[month] if leap_year else MONTH_SEC[month]


def month_days(month: int, leap_year: bool) -> int:
    """
    Get days of the month
    :param month: The month should be 0 <= month <= 13
                   Jan should be 1 and Dec should be 12
    :param leap_year: Is leap year or not
    :return: The days of the month.
    """
    assert 0 <= month <= 13
    return MONTH_DAYS_LEAP_YEAR[month] if leap_year else MONTH_DAYS[month]


# ---------------------------------- Basic Calculation -----------------------------------


def is_leap_year(year: int) -> bool:
    """
    Check whether the year is leap year.
    :param year: Since 0001 or -0001. Can be positive or negative, but not 0.
                  This function will calculate with the absolute value of year.
    :return: True if it's leap year else False
    """
    assert year != 0
    year = abs(int(year))
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def leap_year_count_since_ad(year: int) -> int:
    """
    Concept: Leap year should exclude the 25th, 50th, 75th, keep 100th, exclude 125th, 150th, ...
    :param year: Since 0001 or -0001. Can be positive or negative, but not 0.
                  This function will calculate with the absolute value of year.
    :return: Leap year count that includes this year itself
    """
    assert year != 0
    rough_count = abs(year) // 4
    except_count = rough_count - rough_count // 25 + rough_count // 100
    return except_count


# --------------------------------------- Days ---------------------------------------

# ------------------ xxx -> days ------------------


def years_to_days(year: int) -> int:
    """
    The day of 0001 CE is 0
    The day of 0001 BCE is -365
    The day of 0004 CE the days should be 3 * 365
    The day of 0004 BCE the days should be -(1 + 4 * 365)
    :param year: The year since 0001. It will use absolute value if year is negative.
    :return: The days of years. Considering the leap years. The sign is the same with the year.
    """
    assert year != 0
    sign = 1 if year > 0 else -1
    abs_year = year - 1 if year > 0 else -year
    return sign * (365 * abs_year + abs_year // 4 - abs_year // 100 + abs_year // 400)


def months_to_days(month: int, leap_year: bool) -> int:
    """
    Calculate the days since the beginning of a year to the start of the month. It's not the days of month.
    :param month: The month should be 1 <= month <= 12
    :param leap_year: Is leap year or not
    :return: The days since the beginning of a year to the end of the month, Considering the leap year.
    """
    assert 1 <= month <= 12
    return MONTH_DAYS_SUM_LEAP_YEAR[month - 1] if leap_year else \
        MONTH_DAYS_SUM[month - 1]


def date_to_days(year: int, month: int, day: int) -> int:
    """
    Calculate the days. Note that the day can be larger than the day in month.
    For the BCE date, for example:
        -0001/12/31. The days to CE 0001/01/01 should be -1 * 365 + 334 + 31 - 1 = -1 days.
        -0001/01/01. The days to CE 0001/01/01 should be -1 * 365 + 0 + 1 - 1 = -366 days.
    :param year: Since 0001 CE or 0001 BCE
    :param month: 1 to 12
    :param day: Any
    :return: The days of date since 0001 CE or 0001 BCE
    """
    assert year != 0
    assert 1 <= month <= 12
    days_in_year = years_to_days(year)
    days_in_month = months_to_days(month, is_leap_year(year))
    return days_in_year + days_in_month + (day if year > 0 else day - 1)


# ------------------ days -> xxx ------------------


def days_to_years(days: int) -> (int, int):
    """
    Calculate the years of days since 0001 CE or 0001 BCE.
    :param days: Positive for CE and Negative for BCE.
    :return: The years since 0001 CE or 0001 BCE
    """
    sign = 1 if days >= 0 else -1

    years_400 = (abs(days) - 1) // DAYS_PER_400_YEARS
    remainder = (abs(days) - 1) % DAYS_PER_400_YEARS

    years_100 = remainder // DAYS_PER_100_YEARS
    remainder = remainder % DAYS_PER_100_YEARS

    years_4 = remainder // DAYS_PER_4_YEARS
    remainder = remainder % DAYS_PER_4_YEARS

    if remainder == DAYS_PER_4_YEARS - 1:
        years_1 = 3
        remainder = YEAR_DAYS
    else:
        years_1 = remainder // YEAR_DAYS
        remainder = remainder % YEAR_DAYS

    return sign * (years_400 * 400 + years_100 * 100 + years_4 * 4 + years_1 + 1), remainder + 1


def days_to_months(days: int, leap_year: bool) -> (int, int):
    """
    Calculate the month of days since the beginning of year
    :param days: Days that should be larger than 0 and start with 1 and less than a year
    :param leap_year: Is leap year or not
    :return: The month that since 1 to 12
    """
    assert days > 0
    month_days_sum = MONTH_DAYS_SUM_LEAP_YEAR if leap_year else MONTH_DAYS_SUM
    for month in range(len(month_days_sum)):
        if month_days_sum[month] > days - 1:
            return month, days - month_days_sum[month - 1]
    assert False


def days_to_date(days: int) -> (int, int, int):
    """
    Calculate the date of days since 0001 CE or 0001 BCE
    :param days: Positive for CE and Negative for BCE.
    :return: The date of days
    """
    year, remainder = days_to_years(days)
    leap_year = is_leap_year(year)
    if days < 0:
        remainder = year_days(leap_year) - (remainder - 1)
    month, day = days_to_months(remainder, leap_year)
    return year, month, day


# -------------------------------------- TICK --------------------------------------

# -------------------- xxx -> TICK --------------------


def days_to_tick(days: int) -> int:
    """
    Calculate the seconds of day.
    :param days: Days larger than 0 and start from 1
    :return: The seconds of days
    """
    assert days > 0
    return (days - 1) * TICK_DAY


def months_to_tick(months: int, leap_year: bool) -> int:
    """
    Calculate the seconds of month.
    :param months: 1 - 12
    :param leap_year: Is leap year or not
    :return: The seconds of months
    """
    month_days = months_to_days(months, leap_year)
    return days_to_tick(month_days + 1)


def years_to_tick(year: int) -> int:
    """
    Calculate the seconds since 0001 CE to the start of a positive year
    Or the seconds since 0001 BCE to the head of a negative year
    :param year: Start from 0001 CE or 0001 BCE. Cannot be 0
    :return: The seconds of the years. The sign is the same to the year.
    """
    year_days = years_to_days(year)
    sign = 1 if year_days >= 0 else -1
    return sign * days_to_tick(abs(year_days) + 1)


def date_to_seconds(year: int, month: int, day: int) -> int:
    year_seconds = years_to_tick(year)
    month_seconds = months_to_tick(month, is_leap_year(year))
    day_seconds = days_to_tick(day)
    return year_seconds + month_seconds + day_seconds


def time_data_to_tick(hours: int = 0, minutes: int = 0, seconds: int = 0) -> int:
    """
    Calculate the seconds since the start of day of specified time
    :param hours: 0 - 23
    :param minutes: 0 - 59
    :param seconds: 0 - 59
    :return: The seconds of time
    """
    return hours * TICK_HOUR + minutes * TICK_MIN + seconds


def date_time_data_to_tick(year: int, month: int, day: int,
                           hours: int = 0, minutes: int = 0, seconds: int = 0) -> int:
    date_seconds = date_to_seconds(year, month, day)
    time_seconds = time_data_to_tick(hours, minutes, seconds)
    return date_seconds + time_seconds


# -------------------- TICK -> xxx --------------------


def tick_to_days(tick: int) -> (int, int):
    """
    Convert TICK to days.
    :param tick: The TICK in second. Only positive.
    :return: Tuple of (days, Remainder TICK)
    """
    assert tick >= 0
    return tick // TICK_DAY + 1, tick % TICK_DAY


def tick_to_month(tick: int, leap_year: bool) -> (int, int):
    """
    Convert TICK to month considering the size of the month and leap years
    :param tick: The TICK in second. Only positive.
    :param leap_year: True if leap year else False
    :return: Tuple of (
                Month - Start from 1,
                Remainder of Seconds)
    """
    assert tick >= 0
    days, remainder_sec = tick_to_days(tick)
    months, remainder_days = days_to_months(days, leap_year)
    return months, remainder_sec + days_to_tick(remainder_days)


def tick_to_years(tick: int) -> (int, int):
    """
    Convert TICK to year since CE or BCE
    :param tick: The TICK in second. CE if sec >= 0 else BCE.
    :return: Tuple of (
                Year - Since 0001 CE if sec >= 0 else Since 0001 BCE if sec < 0
                Remainder - Remainder of Seconds that less than a year)
    """
    days, remainder_sec = tick_to_days(abs(tick))
    years, remainder_day = days_to_years(days)
    remainder_sec += (remainder_day - 1) * TICK_DAY
    if tick >= 0:
        return years, remainder_sec
    else:
        # Because the 0 second is assigned to CE. So the BCE should offset 1 second
        result = (-years + 1, 0) if remainder_sec == 0 else \
            (-years, year_ticks(is_leap_year(years)) - remainder_sec)
        return result


def tick_to_date(tick: int) -> (int, int, int, int):
    """
    Convert TICK to year, month, days
    :param tick: The TICK in second. CE if sec >= 0 else BCE.
    :return: Tuple of (year, month, days, Remainder TICK)
    """
    year, remainder = tick_to_years(tick)
    month, remainder = tick_to_month(remainder, is_leap_year(year))
    days, remainder = tick_to_days(remainder)
    return year, month, days, remainder


def tick_to_time_data(tick: int) -> (int, int, int):
    """
    Convert TICK to hours, minutes and seconds
    :param tick: The TICK in second.
    :return: Tuple of (
                Hour - 0 ~ max
                Minutes - 0 ~ 59
                Seconds - 0 ~ 59)
    """
    sec = abs(tick)
    hour = sec // TICK_HOUR
    sec_min = sec % TICK_HOUR
    minute = sec_min // TICK_MIN
    seconds = sec_min % TICK_MIN
    return hour, minute, seconds


def tick_to_date_time_data(tick: int) -> (int, int, int, int, int, int):
    """
    Convert TICK to year, month, days, hours, minutes and seconds
    :param tick: The TICK in second. CE if sec >= 0 else BCE.
    :return: Tuple of (
                year - Year of CE or BCE.
                month - The month in year.
                days - The day in month.
                hour
                minute
                second)
    """
    year, month, days, remainder = tick_to_date(tick)
    hour, minute, second = tick_to_time_data(remainder)
    return year, month, days, hour, minute, second


# -------------------------------------- Time Delta --------------------------------------

def offset_ad_second(tick: TICK, offset: Tuple[int, int, int, int, int, int]) -> TICK:
    """
    Add offset date and time to origin tick.
    :param tick: History tick in second
    :param offset: Tuple of offset (years, months, days, hours, minutes, seconds)
    :return: The history TICK after offset
    """

    offset_year, offset_month, offset_day, offset_hour, offset_minute, offset_second = offset
    tick += offset_day * TICK_DAY + offset_hour * TICK_HOUR + offset_minute * TICK_MIN + offset_second * TICK_SEC
    year, month, day, remainder = tick_to_date(tick)

    month += offset_month
    if month > 0:
        offset_year += (month - 1) // 12
        month = (month - 1) % 12 + 1
    else:
        # If month = -11, then the offset year is -1 and the complement month is  1 (-1 * 12 + 1 = -11)
        # If month = -12, then the offset year is -2 and the complement month is 12 (-2 * 12 + 12 = -12)
        # If month = -13, then the offset year is -2 and the complement month is 11 (-2 * 12 + 11 = -13)
        month_year = abs(month) // 12 + 1
        complement_month = month_year * 12 + month
        offset_year -= month_year
        month = complement_month

    # If year is 1, and offset_year is -1, the result should be -1, because there's no 0 year.
    # So if year is 10, and offset_year is -10, the -1 branch will be reached
    # Else if year is less than 0 or offset_year is larger than 0, the -1 branch will not be reached
    if 0 < year <= -offset_year:
        year += offset_year - 1
    elif -offset_year <= year < 0:
        year += offset_year + 1
    else:
        year += offset_year

    mdays = month_days(month, is_leap_year(year))
    day = min(day, mdays)

    return date_time_data_to_tick(year, month, day, 0, 0, 0) + remainder


def offset_date_time(origin: Tuple[int, int, int, int, int, int],
                     offset: Tuple[int, int, int, int, int, int]) -> Tuple[int, int, int, int, int, int]:
    """
    Add offset date and time to origin date time.
    :param origin: Tuple of (year, month, day, hour, minute, second)
    :param offset: Tuple of offset (years, months, days, hours, minutes, seconds)
    :return: The date time after offset, with tuple format (year, month, day, hour, minute, second)
    """
    offset_datetime = [x + y for x, y in zip(origin, offset)]

    offset_datetime[4] += offset_datetime[5] // 60
    offset_datetime[5] = offset_datetime[5] % 60

    offset_datetime[3] += offset_datetime[4] // 60
    offset_datetime[4] = offset_datetime[4] % 60

    offset_datetime[2] += offset_datetime[3] // 24
    offset_datetime[3] = offset_datetime[3] % 24

    days = date_to_days(offset_datetime[0], offset_datetime[1], offset_datetime[2])
    year, month, day = days_to_date(days)
    return year, month, day, offset_datetime[3], offset_datetime[4], offset_datetime[5]
