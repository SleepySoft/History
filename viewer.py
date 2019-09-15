import traceback, math

from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QLineEdit, QAbstractItemView, QFileDialog, QCheckBox, QWidget, QLabel, QTextEdit, \
    QTabWidget, QComboBox, QGridLayout
from core import *
from Utility.ui_utility import *


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

        self.__prev_pos = None
        self.__l_pressing = False
        self.__l_down_point = None

        self.__era = ''
        self.__since = 0.0
        self.__until = 2000.0
        self.__horizon = False

        self.__scale_start = 0.0
        self.__main_step = 200.0
        self.__sub_step = 20.0

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

    def mouseDoubleClickEvent(self,  event):
        pass

    def mouseMoveEvent(self, event):
        now_pos = event.pos()
        if self.__l_pressing and self.__prev_pos is not None:
            self.__offset = self.__prev_pos.y() - now_pos.y()
            self.repaint()
        self.__prev_pos = now_pos

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
            self.paint_horizon(qp)
        else:
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

        scale_pixels = int(self.__height - TimeAxis.DEFAULT_MARGIN_PIXEL) / 10
        scale_pixels = max(scale_pixels, TimeAxis.MAIN_SCALE_MIN_PIXEL)

        offset_scale = self.__offset / scale_pixels
        offset_scale = int(offset_scale) + 1

        # TODO: Paint offset
        paint_offset = offset_scale * scale_pixels

        for i in range(0, 11):
            y_main = int(scale_pixels * i) + TimeAxis.DEFAULT_MARGIN_PIXEL / 2
            qp.drawLine(main_scale_start, y_main, main_scale_end, y_main)
            for j in range(0, 10):
                y_sub = (y_main + scale_pixels * j / 10)
                qp.drawLine(sub_scale_start, y_sub, sub_scale_end, y_sub)

    # -------------------------------------------------- Calculation ---------------------------------------------------

    def auto_scale(self):
        delta = self.__until - self.__since
        index_10 = math.log(delta, 10)
        rount_index_10 = round(index_10 + 0.5)
        scale = math.pow(10, rount_index_10)

        self.__scale_start = (round(self.__since / scale) + 1) * scale
        self.__main_step = scale / 10
        self.__sub_step = self.__main_step / 10


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


def main():
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


























