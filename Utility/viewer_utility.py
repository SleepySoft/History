from os import sys, path

from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import QRect, QPoint

root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    from Utility.history_time import *
    from Utility.history_public import *
except Exception as e:
    sys.path.append(root_path)
    from Utility.history_time import *
    from Utility.history_public import *
finally:
    pass


# ------------------------------------------------------- Fonts --------------------------------------------------------

event_font = QFont()
event_font.setFamily("微软雅黑")
event_font.setPointSize(6)

period_font = QFont()
period_font.setFamily("微软雅黑")
period_font.setPointSize(8)


# ------------------------------------------------------- Colors -------------------------------------------------------

# From: https://www.icoa.cn/a/512.html

AXIS_BACKGROUND_COLORS = [QColor(255, 245, 247), QColor(254, 67, 101), QColor(252, 157, 154),
                          QColor(249, 205, 173), QColor(200, 200, 169), QColor(131, 175, 155)]
THREAD_BACKGROUND_COLORS = [QColor(182, 194, 154), QColor(138, 151, 123), QColor(244, 208, 0), QColor(229, 87, 18),
                            QColor(178, 200, 187), QColor(69, 137, 148), QColor(117, 121, 74), QColor(114, 83, 52),
                            QColor(130, 57, 53), QColor(137, 190, 178), QColor(201, 211, 140), QColor(222, 156, 83),
                            QColor(160, 90, 124), QColor(101, 147, 74), QColor(64, 116, 52), QColor(222, 125, 44)]

# ------------------------------------------------------ Constant ------------------------------------------------------

LAYOUT_TYPE = int
ALIGN_TYPE = int

LAYOUT_HORIZON = 1
LAYOUT_VERTICAL = 2
ALIGN_LEFT = 4
ALIGN_RIGHT = 8


# ----------------------------------------------------------------------------------------------------------------------
#                                                  class AxisMapping
# ----------------------------------------------------------------------------------------------------------------------

class AxisMapping:
    def __init__(self,
                 range_a_lower: float or int = 0, range_a_upper: float or int = 0,
                 range_b_lower: float or int = 0, range_b_upper: float or int = 0):
        self.__al = range_a_lower
        self.__ah = range_a_upper
        self.__bl = range_b_lower
        self.__bh = range_b_upper

    def set_range_a(self, lower: float or int, upper: float or int):
        self.__al, self.__ah = lower, upper

    def set_range_b(self, lower: float or int, upper: float or int):
        self.__bl, self.__bh = lower, upper

    def set_range_ref(self, ref_a: float or int, ref_b: float or int,
                      origin_a: float or int = 0, origin_b: float or int = 0):
        """
        Config the mapping by the reference length of range a and b.
        :param ref_a: The reference length of range a
        :param ref_b: The reference length of range b
        :param origin_a: The origin (offset) of range a
        :param origin_b: The origin (offset) of range b
        :return: None
        """
        if self.is_digit_zero(ref_a) or self.is_digit_zero(ref_b):
            return
        self.__al, self.__bl = origin_a, origin_b
        # Formula: (bh - bl) / (ah - al) = ref_a / ref_b
        # Assume: ah = al + 1000000
        self.__ah = self.__al + 1000000
        # So: (bh - bl) / 1000000 = ref_a / ref_b
        # Finally: bh = (ref_a / ref_b) * 1000000 + bl
        self.__bh = 1000000 * ref_a / ref_b + self.__bl

    def a_to_b(self, value_a) -> float:
        if self.is_digit_zero(self.__ah - self.__al):
            return 0.0
        return (value_a - self.__al) * (self.__bh - self.__bl) / (self.__ah - self.__al) + self.__bl

    def b_to_a(self, value_b) -> float:
        if self.is_digit_zero((self.__bh - self.__bl)):
            return 0.0
        return (value_b - self.__bl) * (self.__ah - self.__al) / (self.__bh - self.__bl) + self.__al

    @staticmethod
    def is_digit_zero(digit: float or int):
        return digit == 0 if isinstance(digit, int) else digit < 0.0000001


# ----------------------------------------------------------------------------------------------------------------------
#                                                  class AxisMetrics
# ----------------------------------------------------------------------------------------------------------------------

class AxisMetrics:
    def __init__(self):
        self.__scale_since = HistoryTime.TICK(0)
        self.__scale_until = HistoryTime.TICK(0)
        self.__transverse_left = 0
        self.__transverse_right = 0
        self.__longitudinal_since = 0
        self.__longitudinal_until = 0
        self.__align = ALIGN_LEFT
        self.__layout = LAYOUT_VERTICAL

    # ------------------- Gets -------------------

    def get_align(self) -> ALIGN_TYPE:
        return self.__align

    def get_layout(self) -> LAYOUT_TYPE:
        return self.__layout

    def get_scale_range(self) -> (HistoryTime.TICK, HistoryTime.TICK):
        return self.__scale_since, self.__scale_until

    def get_transverse_limit(self) -> (int, int):
        return self.__transverse_left, self.__transverse_right

    def get_longitudinal_range(self) -> (int, int):
        return self.__longitudinal_since, self.__longitudinal_until

    # ------------------- Sets -------------------

    def set_align(self, align: ALIGN_TYPE):
        self.__align = align

    def set_layout(self, layout: LAYOUT_TYPE):
        self.__layout = layout

    def set_scale_range(self, since: HistoryTime.TICK, until: HistoryTime.TICK):
        self.__scale_since = since
        self.__scale_until = until

    def set_transverse_limit(self, left: int, right: int):
        self.__transverse_left = left
        self.__transverse_right = right

    def set_longitudinal_range(self, since: int, _range: int):
        self.__longitudinal_since = since
        self.__longitudinal_until = _range

    # ------------------- Parse -------------------

    def wide(self) -> int:
        return abs(self.__transverse_right - self.__transverse_left)

    def long(self) -> int:
        return abs(self.__longitudinal_until - self.__longitudinal_since)

    def rect(self) -> QRect:
        if self.__layout == LAYOUT_VERTICAL:
            rect = QRect(self.__transverse_left, self.__longitudinal_since,
                         self.__transverse_right - self.__transverse_left,
                         self.__longitudinal_until - self.__longitudinal_since)
        else:
            rect = QRect(self.__longitudinal_since, self.__transverse_right,
                         self.__longitudinal_until - self.__longitudinal_since,
                         self.__transverse_left - self.__transverse_right)
        return rect

    def copy(self, rhs):
        self.__scale_since = rhs.__scale_since
        self.__scale_until = rhs.__scale_until
        self.__transverse_left = rhs.__transverse_left
        self.__transverse_right = rhs.__transverse_right
        self.__longitudinal_since = rhs.__longitudinal_since
        self.__longitudinal_until = rhs.__longitudinal_until
        self.__align = rhs.__align
        self.__layout = rhs.__layout

    def offset(self, long_offset: int, wide_offset: int):
        self.__longitudinal_since += long_offset
        self.__longitudinal_until += wide_offset
        self.__transverse_left += wide_offset
        self.__transverse_right += wide_offset

    def contains(self, point: QPoint) -> bool:
        return self.rect().contains(point)

    def adjust_area(self, area: QRect) -> QRect:
        if self.__layout == LAYOUT_VERTICAL:
            if area.top() < self.__longitudinal_since:
                area.setTop(self.__longitudinal_since)
            if area.bottom() > self.__longitudinal_until:
                area.setBottom(self.__longitudinal_until)
        elif self.__layout == LAYOUT_HORIZON:
            if area.left() < self.__longitudinal_since:
                area.setLeft(self.__longitudinal_since)
            if area.right() > self.__longitudinal_until:
                area.setRight(self.__longitudinal_until)
        return area

    def value_to_pixel(self, value: HistoryTime.TICK):
        scale_delta = self.__scale_until - self.__scale_since
        if scale_delta == 0:
            return 0
        return (self.__longitudinal_until - self.__longitudinal_since) * (value - self.__scale_since) / scale_delta


# ----------------------------------------------------------------------------------------------------------------------
#                                                  class TrackContext
# ----------------------------------------------------------------------------------------------------------------------

class TrackContext:
    def __init__(self):
        self.__metrics = None
        self.__layout_bars = []

    def get_metrics(self) -> AxisMetrics:
        return self.__metrics

    def set_metrics(self, metrics: AxisMetrics):
        self.__metrics = metrics

    def get_layout_bars(self) -> []:
        return self.__layout_bars

    def has_space(self, since: int, until: int) -> bool:
        for bar in self.__layout_bars:
            exist_since_pixel, exist_until_pixel = bar.get_item_metrics().get_longitudinal_range()
            if exist_since_pixel < since < exist_until_pixel or \
                    exist_since_pixel < until < exist_until_pixel:
                return False
        return True

    def has_space_for(self, bar) -> bool:
        return self.has_space(*bar.get_longitudinal_space())

    def take_space_for(self, bar):
        if bar in self.__layout_bars:
            self.__layout_bars.remove(bar)
        self.__layout_bars.append(bar)




















