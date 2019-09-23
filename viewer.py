import random
import traceback, math

from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QLineEdit, QAbstractItemView, QFileDialog, QCheckBox, QWidget, QLabel, QTextEdit, \
    QTabWidget, QComboBox, QGridLayout
from core import *
from Utility.ui_utility import *


def upper_rough(num):
    abs_num = abs(num)
    index_10 = math.log(abs_num, 10)
    round_index_10 = math.floor(index_10)
    scale = math.pow(10, round_index_10)
    if num >= 0:
        integer = math.ceil(abs_num / scale)
    else:
        integer = math.floor(abs_num / scale)
    rough = integer * scale
    result = rough if num >= 0 else -rough
    return result


def lower_rough(num):
    abs_num = abs(num)
    if abs_num == 0:
        return 0
    index_10 = math.log(abs_num, 10)
    round_index_10 = math.floor(index_10)
    scale = math.pow(10, round_index_10)
    if num >= 0:
        integer = math.floor(abs_num / scale)
    else:
        integer = math.ceil(abs_num / scale)
    rough = integer * scale
    result = rough if num >= 0 else -rough
    return result


def scale_round(num: float, scale: float):
    return (round(num / scale) + 1) * scale


# --------------------------------------------------- class TimeAxis ---------------------------------------------------

class TimeAxis(QWidget):

    class Thread:
        def __init__(self):
            self.__event_indexes = []
            self.__paint_indexes = []
            self.__indexes_layout = []
            self.__since = 0.0
            self.__until = 0.0
            self.__horizon = False
            self.__thread_width = 0
            self.__thread_length = 0
            self.__thread_track_count = 0
            self.__thread_track_width = 50
            # self.__value_pixel_coeff = 0.0
            self.__paint_area = QRect(0, 0, 0, 0)
            self.__paint_color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        def set_thread_horizon(self, horizon: bool):
            self.__horizon = horizon
            self.calc_paint_parameters()

        def set_thread_event_indexes(self, indexes: list):
            self.__event_indexes = indexes
            self.calc_paint_parameters()

        def on_paint_canvas_size_update(self, area: QRect):
            self.__paint_area = area
            self.calc_paint_parameters()

        def on_paint_scale_range_updated(self, since: float, until: float):
            self.__since = since
            self.__until = until
            self.calc_paint_parameters()

        def calc_paint_parameters(self):
            if self.__horizon:
                self.__thread_width = self.__paint_area.height()
                self.__thread_length = self.__paint_area.width()
            else:
                self.__thread_width = self.__paint_area.width()
                self.__thread_length = self.__paint_area.height()
            self.__thread_track_count = int(self.__thread_width / self.__thread_track_width)

            self.__paint_indexes.clear()
            for index in self.__event_indexes:
                if index.adapt(self.__since, self.__until):
                    self.__paint_indexes.append(index)
            sorted(self.__paint_indexes, key=lambda x: x.since())

            self.layout_event_to_track()

        def layout_event_to_track(self):
            track_list = []
            for i in range(0, self.__thread_track_count):
                track_list.append(self.__since)

            self.__indexes_layout.clear()
            for index in self.__paint_indexes:
                for i in range(0, self.__thread_track_count):
                    # Default layout to the last track
                    if index.since() > track_list[i] or (i == self.__thread_track_count - 1):
                        self.__indexes_layout.append(i)
                        track_list[i] = index.until()
                        break

        def value_to_pixel(self, value: float):
            if self.__until - self.__since == 0:
                return 0
            return self.__thread_length * (value - self.__since) / (self.__until - self.__since)

        def repaint(self, qp: QPainter):
            qp.setBrush(self.__paint_color)
            qp.drawRect(self.__paint_area)
            # if self.__horizon:
            #     self.paint_horizon(qp)
            # else:
            #     self.paint_vertical(qp)

        def paint_horizon(self):
            pass

        def paint_vertical(self, qp: QPainter):
            for track, index in zip(self.__indexes_layout, self.__paint_indexes):
                left = self.__paint_area.left() + track * self.__thread_track_width
                right = left + self.__thread_track_width
                top = self.__paint_area.top() + self.value_to_pixel(index.since())
                bottom = self.__paint_area.top() + self.value_to_pixel(index.until())
                index_rect = QRect(left, top, right - left, bottom - top)
                qp.drawRect(index_rect)


    STEP_LIST = [
        10000, 5000, 2500, 2000, 1000, 500, 250, 200, 100, 50, 25, 20, 10, 5, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01
    ]

    DEFAULT_MARGIN_PIXEL = 0
    MAIN_SCALE_MIN_PIXEL = 50

    def __init__(self):
        super(TimeAxis, self).__init__()

        self.__width = 0
        self.__height = 0
        self.__axis_width = 0
        self.__axis_length = 0

        self.__axis_mid = 0
        self.__axis_space_w = 30
        self.__axis_align_offset = 0.3

        self.__thread_width = 0
        self.__thread_left_area = QRect(0, 0, 0, 0)
        self.__thread_right_area = QRect(0, 0, 0, 0)

        self.__offset = 0.0
        self.__scroll = 0.0

        self.__scale_per_page = 10
        self.__pixel_per_scale = 0

        self.__paint_since = 0
        self.__paint_until = 0
        self.__paint_start_scale = 0
        self.__paint_start_offset = 0

        self.__l_pressing = False
        self.__l_down_point = None

        self.__era = ''
        self.__horizon = False

        self.__step_selection = 0
        self.__main_step = 0
        self.__sub_step = 0

        self.setMinimumWidth(400)
        self.setMinimumHeight(500)

        self.set_time_range(0, 2000)

        # self.setMouseTracking(True)

        self.__history_threads = []

    # ----------------------------------------------------- Method -----------------------------------------------------

    def set_era(self, era: str):
        self.__era = era

    def set_horizon(self):
        self.__horizon = True

    def set_vertical(self):
        self.__horizon = False

    def set_time_range(self, since: float, until: float):
        self.auto_scale(min(since, until), max(since, until))
        self.repaint()

    def get_history_threads(self) -> list:
        return self.__history_threads

    def add_history_thread(self, thread):
        if thread not in self.__history_threads:
            self.__history_threads.append(thread)

    def remove_history_threads(self, thread):
        if thread in self.__history_threads:
            self.__history_threads.remove(thread)

    # --------------------------------------------------- UI Action ----------------------------------------------------

    def mousePressEvent(self,  event):
        if event.button() == QtCore.Qt.LeftButton:
            self.__l_pressing = True
            self.__l_down_point = event.pos()

    def mouseReleaseEvent(self,  event):
        if event.button() == QtCore.Qt.LeftButton:
            self.__l_pressing = False
            self.__scroll += self.__offset
            self.__offset = 0
            self.repaint()

    def mouseDoubleClickEvent(self,  event):
        pass

    def mouseMoveEvent(self, event):
        now_pos = event.pos()
        if self.__l_pressing and self.__l_down_point is not None:
            if self.__horizon:
                self.__offset = self.__l_down_point.x() - now_pos.x()
            else:
                self.__offset = self.__l_down_point.y() - now_pos.y()
            self.repaint()
        pixel_scale_value = self.pixel_offset_to_scale_value(now_pos.y())
        print('Time : ' + str(pixel_scale_value))

    def wheelEvent(self, event):
        angle = event.angleDelta() / 8
        angle_x = angle.x()
        angle_y = angle.y()

        modifiers = QApplication.keyboardModifiers()

        if modifiers == QtCore.Qt.ControlModifier:
            # Get the value before step update
            current_pos = event.pos()
            current_pos_offset = self.calc_point_to_paint_start_offset(current_pos)
            current_pos_scale_value = self.pixel_offset_to_scale_value(current_pos_offset)

            self.select_step_scale(self.__step_selection + (1 if angle_y < 0 else -1))

            # Make the value under mouse keep the same place on the screen
            total_pixel_offset = self.__pixel_per_scale * current_pos_scale_value / self.__main_step
            total_pixel_offset -= current_pos_offset
            self.__scroll = total_pixel_offset - self.__offset
        else:
            self.__scroll += (1 if angle_y < 0 else -1) * self.__pixel_per_scale / 4

        self.repaint()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        wnd_size = self.size()
        self.__width = wnd_size.width()
        self.__height = wnd_size.height()

        self.__axis_width = self.__height if self.__horizon else self.__width
        self.__axis_length = self.__width if self.__horizon else self.__height
        self.__axis_length -= self.DEFAULT_MARGIN_PIXEL * 2

        self.update_pixel_per_scale()
        self.calc_paint_parameters()
        self.calc_paint_layout()

        self.paint_background(qp)

        if self.__horizon:
            self.paint_horizon(qp)
        else:
            self.paint_vertical(qp)
        self.paint_threads(qp)

        qp.end()

    # ----------------------------------------------------- Paint ------------------------------------------------------

    def paint_background(self, qp: QPainter):
        qp.setBrush(QColor(100, 0, 0))
        qp.drawRect(0, 0, self.__width, self.__height)

    def paint_horizon(self, qp: QPainter):
        pass

    def paint_vertical(self, qp: QPainter):
        qp.drawLine(self.__axis_mid, 0, self.__axis_mid, self.__height)

        main_scale_start = int(self.__axis_mid - 15)
        main_scale_end = int(self.__axis_mid + 15)
        sub_scale_start = int(self.__axis_mid - 5)
        sub_scale_end = int(self.__axis_mid + 5)

        for i in range(0, 12):
            y_main = int(self.__pixel_per_scale * i) - self.__paint_start_offset + TimeAxis.DEFAULT_MARGIN_PIXEL
            time_main = (self.__paint_start_scale + i) * self.__main_step
            qp.drawLine(main_scale_start, y_main, main_scale_end, y_main)
            qp.drawText(main_scale_end - 100, y_main, str(time_main))
            for j in range(0, 10):
                y_sub = int(y_main + self.__pixel_per_scale * j / 10)
                qp.drawLine(sub_scale_start, y_sub, sub_scale_end, y_sub)

    def paint_threads(self, qp: QPainter):
        for thread in self.__history_threads:
            thread.repaint(qp)

    # -------------------------------------------------- Calculation ---------------------------------------------------

    def calc_point_to_paint_start_offset(self, point):
        if self.__horizon:
            return point.x() - TimeAxis.DEFAULT_MARGIN_PIXEL
        else:
            return point.y() - TimeAxis.DEFAULT_MARGIN_PIXEL

    def update_pixel_per_scale(self):
        self.__pixel_per_scale = self.__axis_length / self.__scale_per_page
        self.__pixel_per_scale = max(self.__pixel_per_scale, TimeAxis.MAIN_SCALE_MIN_PIXEL)

    def calc_paint_parameters(self):
        total_pixel_offset = self.__scroll + self.__offset

        self.__paint_since = float(total_pixel_offset) / self.__pixel_per_scale
        self.__paint_until = self.__paint_since + self.__axis_length / self.__pixel_per_scale

        self.__paint_start_scale = math.floor(self.__paint_since)
        self.__paint_start_offset = total_pixel_offset - self.__paint_start_scale * self.__pixel_per_scale

    def calc_paint_layout(self):
        self.__axis_mid = int(self.__axis_width * self.__axis_align_offset)

        threads_count = len(self.__history_threads)
        if threads_count == 0:
            return

        left_thread_count = int(threads_count * self.__axis_align_offset + 0.5)
        right_thread_count = threads_count - left_thread_count

        axis_left_margin = self.__axis_mid - self.__axis_space_w / 2
        axis_right_margin = self.__axis_mid + self.__axis_space_w / 2

        if left_thread_count > 0:
            left_thread_width = axis_left_margin / left_thread_count
        else:
            left_thread_width = 0

        if right_thread_count > 0:
            right_thread_width = (self.__axis_width - axis_right_margin) / right_thread_count
        else:
            right_thread_width = 0

        # Vertical -> Horizon : Left rotate
        for i in range(0, threads_count):
            thread = self.__history_threads[i]
            if self.__horizon:
                pass
            else:
                top = TimeAxis.DEFAULT_MARGIN_PIXEL
                bottom = self.__axis_length - TimeAxis.DEFAULT_MARGIN_PIXEL
                if i < left_thread_count:
                    left = i * left_thread_width
                    area = QRect(QPoint(left, top), QPoint(left + left_thread_width, bottom))
                    thread.on_paint_canvas_size_update(area)
                else:
                    left = axis_right_margin + (i - left_thread_count) * right_thread_width
                    area = QRect(QPoint(left, top), QPoint(left + right_thread_width, bottom))
                    thread.on_paint_canvas_size_update(area)

    def pixel_offset_to_scale_value(self, display_pixel_offset: int) -> float:
        delta_pixel_offset = display_pixel_offset + self.__paint_start_offset - self.DEFAULT_MARGIN_PIXEL
        delta_scale_offset = delta_pixel_offset / self.__pixel_per_scale
        return (self.__paint_start_scale + delta_scale_offset) * self.__main_step

    def auto_scale(self, since: float, until: float):
        since_rough = lower_rough(since)
        until_rough = upper_rough(until)
        delta = until_rough - since_rough
        delta_rough = upper_rough(delta)
        step_rough = delta_rough / 10

        step_index = 1
        while step_index < len(TimeAxis.STEP_LIST):
            if TimeAxis.STEP_LIST[step_index] < step_rough:
                break
            step_index += 1
        self.select_step_scale(step_index - 1)

        self.update_pixel_per_scale()
        self.__scroll = since_rough * self.__pixel_per_scale

    def select_step_scale(self, step_index: int):
        self.__step_selection = step_index
        self.__step_selection = max(self.__step_selection, 0)
        self.__step_selection = min(self.__step_selection, len(TimeAxis.STEP_LIST) - 1)

        self.__main_step = TimeAxis.STEP_LIST[self.__step_selection]
        self.__sub_step = self.__main_step / 10

        # abs_num = abs(num)
        # if abs_num >= 100:
        #     index_10 = math.log(abs_num, 10)
        #     round_index_10 = math.floor(index_10)
        #     scale = math.pow(10, round_index_10)
        #     delta = scale / 10
        # elif 10 < abs_num < 100:
        #     delta = 10
        # elif 1 < abs_num <= 10:
        #     delta = 1
        # else:
        #     if sign > 0:
        #         delta = 1
        #     else:
        #         delta = 0
        # return sign * delta * ratio

    def notify_scale_updated(self, since: float, until: float):
        pass


# ------------------------------------------------- class HistoryViewer ------------------------------------------------
#
# class HistoryViewer(QWidget):
#     def __init__(self):
#         super(HistoryViewer, self).__init__()
#
#         self.__axis = TimeAxis()
#
#         root_layout = QHBoxLayout()
#         self.setLayout(root_layout)
#
#         root_layout.addWidget(self.__axis)
#
#     def paintEvent(self, event):
#         qp = QPainter()
#         qp.begin(self)
#         qp.end()


# ---------------------------------------------------- Test ------------------------------------------------------------

def test_upper_rough():
    assert math.isclose(upper_rough(10001), 20000)
    assert math.isclose(upper_rough(10000), 10000)
    assert math.isclose(upper_rough(9999), 10000)
    assert math.isclose(upper_rough(9001), 10000)
    assert math.isclose(upper_rough(8999),  9000)
    assert math.isclose(upper_rough(1.1), 2)
    # assert math.isclose(upper_rough(0.07), 0.07)

    assert math.isclose(upper_rough(-10001), -10000)
    assert math.isclose(upper_rough(-10000), -10000)
    assert math.isclose(upper_rough(-9999), -9000)
    assert math.isclose(upper_rough(-9001), -9000)
    assert math.isclose(upper_rough(-8999), -8000)
    assert math.isclose(upper_rough(-1.1), -1.0)
    # assert math.isclose(upper_rough(-0.07), 0.07)


def test_lower_rough():
    assert math.isclose(lower_rough(10001), 10000)
    assert math.isclose(lower_rough(10000), 10000)
    assert math.isclose(lower_rough(9999), 9000)
    assert math.isclose(lower_rough(9001), 9000)
    assert math.isclose(lower_rough(8999),  8000)
    assert math.isclose(lower_rough(1.1), 1.0)
    # assert math.isclose(lower_rough(0.07), 0.07)

    assert math.isclose(lower_rough(-10001), -20000)
    assert math.isclose(lower_rough(-10000), -10000)
    assert math.isclose(lower_rough(-9999), -10000)
    assert math.isclose(lower_rough(-9001), -10000)
    assert math.isclose(lower_rough(-8999), -9000)
    assert math.isclose(lower_rough(-1.1), -2.0)
    # assert math.isclose(upper_rough(-0.07), 0.07)


def main():
    test_upper_rough()
    test_lower_rough()

    app = QApplication(sys.argv)

    time_axis = TimeAxis()

    import indexer
    idxer = indexer.EventIndexer()
    idxer.load_from_file('history.index')
    idxer.print_indexes()

    for i in range(0, 6):
        time_axis.add_history_thread(TimeAxis.Thread())

    # thread = TimeAxis.Thread()
    # thread.set_thread_event_indexes(idxer.get_indexes())
    # time_axis.add_history_thread(thread)

    layout = QVBoxLayout()
    layout.addWidget(time_axis)

    dlg = QDialog()
    dlg.setLayout(layout)
    dlg.exec()


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


























