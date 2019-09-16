import traceback, math

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


class TimeAxis(QWidget):

    DEFAULT_MARGIN_PIXEL = 10
    MAIN_SCALE_MIN_PIXEL = 50

    def __init__(self):
        super(TimeAxis, self).__init__()

        self.__width = 0
        self.__height = 0

        self.__offset = 0.0
        self.__scroll = 0.0
        self.__scale_pixel = 0.0

        self.__l_pressing = False
        self.__l_down_point = None
        self.__move_prev_point = None

        self.__era = ''
        self.__since = 0.0
        self.__until = 2000.0
        self.__horizon = False

        self.__scale_start = 0.0
        self.__main_step = 200.0
        self.__sub_step = 20.0

        self.setMinimumWidth(400)
        self.setMinimumHeight(500)

    # ----------------------------------------------------- Method -----------------------------------------------------

    def set_era(self, era: str):
        self.__era = era

    def set_horizon(self):
        self.__horizon = True

    def set_vertical(self):
        self.__horizon = False

    def set_time_range(self, since: float, until: float):
        self.__since = min(since, until)
        self.__until = max(since, until)
        if self.__until == self.__since:
            self.__since -= 1
            self.__until += 1
        self.auto_scale()
        self.repaint()

    # --------------------------------------------------- UI Action ----------------------------------------------------

    def mousePressEvent(self,  event):
        if event.button() == QtCore.Qt.LeftButton:
            self.__l_pressing = True
            self.__l_down_point = event.pos()

    def mouseReleaseEvent(self,  event):
        if event.button() == QtCore.Qt.LeftButton:
            self.__l_pressing = False
            self.__l_down_point = event.pos()
            self.__scroll += self.__offset
            self.__offset = 0
            self.repaint()

    def mouseDoubleClickEvent(self,  event):
        pass

    def mouseMoveEvent(self, event):
        now_pos = event.pos()
        if self.__l_pressing and self.__move_prev_point is not None:
            self.__offset += self.__move_prev_point.y() - now_pos.y()
            self.repaint()
        self.__move_prev_point = now_pos

    def wheelEvent(self, event):
        angle = event.angleDelta() / 8
        angle_x = angle.x()
        angle_y = angle.y()

        # delta_step_pct = angle_y / 1.5 / 100

        # if delta_step_pct > 0:
        #     new_main_step = self.__main_step * (1 + delta_step_pct)
        # else:
        #     new_main_step = self.__main_step / (1 - delta_step_pct)
        #
        # print('delta_step_pct = ' + str(delta_step_pct) + ', new_main_step = ' + str(new_main_step))

        self.__main_step = self.auto_increase(self.__main_step, 1 if angle_y < 0 else -1, 1)

        # if self.__main_step >= 100:
        #     self.__main_step = self.auto_increase(self.__main_step, 1 if angle_y > 0 else -1, 2)
        # else:
        #     self.__main_step += 10 if angle_y > 0 else -10

        self.__sub_step = self.__main_step / 10
        self.repaint()

    # ----------------------------------------------------- Paint ------------------------------------------------------

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        wnd_size = self.size()
        self.__width = wnd_size.width()
        self.__height = wnd_size.height()
        print(wnd_size)

        self.paint_background(qp)

        if self.__horizon:
            self.calc_paint_parameters(self.__width)
            self.paint_horizon(qp)
        else:
            self.calc_paint_parameters(self.__height)
            self.paint_vertical(qp)
        qp.end()

    def paint_background(self, qp: QPainter):
        qp.setBrush(QColor(100, 0, 0))
        qp.drawRect(0, 0, self.__width, self.__height)

    def paint_horizon(self, qp: QPainter):
        pass

    def paint_vertical(self, qp: QPainter):
        axis_mid = self.__width * 3 / 10
        qp.drawLine(axis_mid, 0, axis_mid, self.__height)

        main_scale_start = int(axis_mid - 15)
        main_scale_end = int(axis_mid + 15)
        sub_scale_start = int(axis_mid - 5)
        sub_scale_end = int(axis_mid + 5)

        for i in range(0, 11):
            y_main = int(self.__scale_pixel * i) + TimeAxis.DEFAULT_MARGIN_PIXEL / 2 - self.__scroll
            time_main = self.__since + i * self.__main_step
            qp.drawLine(main_scale_start, y_main, main_scale_end, y_main)
            qp.drawText(main_scale_end - 100, y_main, str(time_main))
            for j in range(0, 10):
                y_sub = (y_main + self.__scale_pixel * j / 10)
                qp.drawLine(sub_scale_start, y_sub, sub_scale_end, y_sub)

    # -------------------------------------------------- Calculation ---------------------------------------------------

    def calc_paint_parameters(self, total_len: int):
        self.__scale_pixel = int(total_len - TimeAxis.DEFAULT_MARGIN_PIXEL) / 10
        self.__scale_pixel = max(self.__scale_pixel, TimeAxis.MAIN_SCALE_MIN_PIXEL)

        pixel_offset = self.__scroll + self.__offset

        scale_offset = math.floor(pixel_offset / self.__scale_pixel)
        paint_offset = pixel_offset % self.__scale_pixel

        self.__offset = 0
        self.__since -= scale_offset
        self.__scroll = paint_offset

    def auto_scale(self):
        since_rough = lower_rough(self.__since)
        until_rough = upper_rough(self.__until)
        delta = until_rough - since_rough
        delta_rough = upper_rough(delta)

        self.__scale_start = since_rough
        self.__main_step = delta_rough / 10
        self.__sub_step = self.__main_step / 10

    def auto_increase(self, num, sign, ratio):
        """
        Increase the number by 10% of its index.
        :param num: The number you want to increase.
        :param sign: 1 or -1.
        :param ratio: The ratio to multiple 10% of its index.
        :return:
        """
        abs_num = abs(num)
        if abs_num >= 100:
            index_10 = math.log(abs_num, 10)
            round_index_10 = math.floor(index_10)
            scale = math.pow(10, round_index_10)
            delta = scale / 10
        elif 10 < abs_num < 100:
            delta = 10
        elif 1 < abs_num <= 10:
            delta = 1
        else:
            delta = 0
        return num + sign * delta * ratio


class HistoryViewer(QWidget):
    def __init__(self):
        super(HistoryViewer, self).__init__()

        self.__axis = TimeAxis()

        root_layout = QHBoxLayout()
        self.setLayout(root_layout)

        root_layout.addWidget(self.__axis)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.end()


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

    layout = QVBoxLayout()
    layout.addWidget(HistoryViewer())

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


























