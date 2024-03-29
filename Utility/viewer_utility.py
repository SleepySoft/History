import sys
import math
from os import path

from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import QRect, QPoint

root_path = path.dirname(path.dirname(path.abspath(__file__)))

try:
    from Utility import HistoryTime
    from Utility.history_public import *
except Exception as e:
    sys.path.append(root_path)
    from Utility import HistoryTime
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
    """
    处理从范围A到范围B的映射。

    m = AxisMapping(10, 40, 0, 3000)    # A的范围是(10, 40), b的范围是(0 - 3000)

    assert m.a_to_b(10) == 0            # A范围内的值10映射到B范围内的0
    assert m.b_to_a(0) == 10            # 相应的B范围内的值0映射到A范围内10

    assert m.a_to_b(25) == 1500         # A范围内的值25映射到B范围内的1500
    assert m.b_to_a(1500) == 25         # 相应的B范围内的值1500映射到A范围内25

    assert m.a_to_b(40) == 3000         # A范围内的值40映射到B范围内的3000
    assert m.b_to_a(3000) == 40         # 相应的B范围内的值3000映射到A范围内40
    """
    def __init__(self,
                 range_a_lower: float or int = 0, range_a_upper: float or int = 0,
                 range_b_lower: float or int = 0, range_b_upper: float or int = 0):
        self.__al = range_a_lower
        self.__ar = range_a_upper - range_a_lower
        self.__bl = range_b_lower
        self.__br = range_b_upper - range_b_lower

    def set_range_a(self, lower: float or int, upper: float or int):
        self.__al = lower
        self.__ar = upper - lower

    def set_range_b(self, lower: float or int, upper: float or int):
        self.__bl = lower
        self.__br = upper - lower

    def set_range_ref(self, ref_a: float or int, ref_b: float or int,
                      origin_a: float or int = 0, origin_b: float or int = 0):
        """
        通过参考长度和原点来配置映射。
        :param ref_a: 范围A的参考长度
        :param ref_b: 范围B的参考长度
        :param origin_a: 范围A的原点（偏移量）
        :param origin_b: 范围B的原点（偏移量）
        :return: None

        这个方法允许你通过指定两个范围的参考长度和原点来配置数值映射。参考长度定义了每个范围的大小，原点定义了每个范围的起始位置。
        例如，如果你想将一个0-10的范围映射到一个100-200的范围，你可以这样调用这个方法：set_range_ref(10, 100, 0, 100)。
        这样，一个在范围A中的数值x将被映射到范围B中的数值y，其中y = (x / 10) * 100 + 100。
        """
        self.__al, self.__ar = origin_a, ref_a
        self.__bl, self.__br = origin_b, ref_b

    def a_to_b(self, value_a) -> float:
        return 0.0 if self.is_digit_zero(self.__ar) else (value_a - self.__al) * self.__br / self.__ar + self.__bl

    def b_to_a(self, value_b) -> float:
        return 0.0 if self.is_digit_zero(self.__br) else (value_b - self.__bl) * self.__ar / self.__br + self.__al

    @staticmethod
    def is_digit_zero(digit: float or int):
        return math.isclose(digit, 0, abs_tol=1e-9)


# ----------------------------------------------------------------------------------------------------------------------
#                                                  class AxisMetrics
# ----------------------------------------------------------------------------------------------------------------------

class AxisMetrics:
    """
    将Item区域表征抽象为“横（transverse）”和“纵（longitudinal）”，
    它与Rect的left, top, right, bottom对应如下：
    当布局为纵向时，transverse_left, longitudinal_since, transverse_right, longitudinal_until
    当布局为横向时，longitudinal_since, transverse_right, longitudinal_until, transverse_left
    图示：

                  longitudinal_since
                        ┌────┐
        transverse_left │    │     ----Flip counterclockwise---->        transverse_right
                        │    │                                          ┌────────────────┐
                        │    │                       longitudinal_since │                │ longitudinal_until
                        │    │                                          └────────────────┘
                        │    │ transverse_right                           transverse_left
                        └────┘
                  longitudinal_until

    """
    def __init__(self):
        self.__scale_since = HistoryTime.TICK(0)
        self.__scale_until = HistoryTime.TICK(0)
        self.__transverse_left = 0
        self.__transverse_right = 0
        self.__longitudinal_since = 0
        self.__longitudinal_until = 0
        self.__align = ALIGN_LEFT
        self.__layout = LAYOUT_VERTICAL
        self.__value_pixel_mapping = AxisMapping()

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

    def get_transverse_length(self) -> int:
        return abs(self.__transverse_right - self.__transverse_left)

    def get_longitudinal_length(self) -> int:
        return abs(self.__longitudinal_until - self.__longitudinal_since)

    # ------------------- Sets -------------------

    def set_align(self, align: ALIGN_TYPE):
        self.__align = align

    def set_layout(self, layout: LAYOUT_TYPE):
        self.__layout = layout

    def set_scale_range(self, since: HistoryTime.TICK, until: HistoryTime.TICK):
        self.__scale_since = since
        self.__scale_until = until
        self.__value_pixel_mapping.set_range_a(since, until)

    def set_transverse_limit(self, left: int, right: int):
        self.__transverse_left = left
        self.__transverse_right = right

    def set_longitudinal_range(self, since: int, until: int):
        self.__longitudinal_since = since
        self.__longitudinal_until = until
        self.__value_pixel_mapping.set_range_b(since, until)

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
        self.__value_pixel_mapping.set_range_a(self.__scale_since, self.__scale_until)
        self.__value_pixel_mapping.set_range_b(self.__longitudinal_since, self.__longitudinal_until)

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

    def value_to_pixel(self, value: HistoryTime.TICK) -> int:
        return int(self.__value_pixel_mapping.a_to_b(value))
        # scale_delta = self.__scale_until - self.__scale_since
        # if scale_delta == 0:
        #     return 0
        # return (self.__longitudinal_until - self.__longitudinal_since) * (value - self.__scale_since) / scale_delta

    def pixel_to_value(self, pixel: int) -> HistoryTime.TICK:
        return HistoryTime.TICK(self.__value_pixel_mapping.b_to_a(pixel))


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

    def has_space(self, since: HistoryTime.TICK, until: HistoryTime.TICK) -> bool:
        for bar in self.__layout_bars:
            exist_since_tick, exist_until_tick = bar.get_item_metrics().get_scale_range()
            if exist_since_tick < since < exist_until_tick or \
                    exist_since_tick < until < exist_until_tick:
                return False
        return True

    def take_space_for(self, bar):
        if bar in self.__layout_bars:
            self.__layout_bars.remove(bar)
        self.__layout_bars.append(bar)

