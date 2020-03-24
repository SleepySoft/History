import copy
import time
import random
import traceback, math
from PyQt5.QtCore import QRect, QPoint, QSize
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPolygon, QFontMetrics

from os import sys, path
root_path = path.dirname(path.dirname(path.abspath(__file__)))


try:
    from viewer_ex import *
    from Utility.history_time import *
    from Utility.viewer_utility import *
except Exception as e:
    sys.path.append(root_path)

    from viewer_ex import *
    from Utility.history_time import *
    from Utility.viewer_utility import *
finally:
    pass


# ----------------------------------------------------------------------------------------------------------------------
#                                                  class Candlestick
# ----------------------------------------------------------------------------------------------------------------------

class Candlestick(AxisItem):
    COLOR_INCREASE = QColor(255, 0, 0)
    COLOR_DECREASE = QColor(0, 255, 0)

    def __init__(self, upper_limit: float, lower_limit: float,
                 date: HistoryTime.TICK, _open: float, close: float, high: float, low: float):
        super(Candlestick, self).__init__(None, {})
        self.__upper_limit = upper_limit
        self.__lower_limit = lower_limit
        self.__date = date
        self.__open = _open
        self.__close = close
        self.__high = high
        self.__low = low

        metrics = self.get_item_metrics()
        metrics.set_scale_range(date, date + HistoryTime.day(1) - 1)

    def get_tip_text(self, on_tick: float) -> str:
        return ''

    def paint(self, qp: QPainter):
        if self.get_outer_metrics().get_layout() == LAYOUT_HORIZON:
            self.__paint_horizon(qp)
        elif self.get_outer_metrics().get_layout() == LAYOUT_VERTICAL:
            self.__paint_vertical(qp)

    def __paint_horizon(self, qp: QPainter):
        metrics = self.get_item_metrics()
        item_rect = metrics.rect()

        limit_range = self.__upper_limit - self.__lower_limit
        open_y = item_rect.bottom() + item_rect.height() * (self.__open - self.__lower_limit) / limit_range
        close_y = item_rect.bottom() + item_rect.height() * (self.__close - self.__lower_limit) / limit_range
        high_y = item_rect.bottom() + item_rect.height() * (self.__high - self.__lower_limit) / limit_range
        low_y = item_rect.bottom() + item_rect.height() * (self.__low - self.__lower_limit) / limit_range

        item_rect.setTop(open_y)
        item_rect.setBottom(close_y)

        mid_x = item_rect.center().x()
        color = Candlestick.COLOR_INCREASE if self.__close > self.__open else Candlestick.COLOR_DECREASE

        qp.setPen(color)
        qp.setBrush(color)
        qp.drawLine(mid_x, high_y, mid_x, low_y)
        qp.drawRect(item_rect)

    def __paint_vertical(self, qp: QPainter):
        pass


# ----------------------------------------------------- File Entry -----------------------------------------------------

def main():
    app = QApplication(sys.argv)

    # Threads
    thread = TimeThreadBase()
    thread.set_thread_color(THREAD_BACKGROUND_COLORS[0])

    # CandleSticks
    date = HistoryTime.now_tick() - HistoryTime.year(1)
    for i in range(100):
        date += HistoryTime.day(1)
        cs = Candlestick(0, 5000, )


    # HistoryViewerDialog
    history_viewer = HistoryViewerDialog()
    history_viewer.get_time_axis().add_history_thread(thread)
    history_viewer.exec()


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






















