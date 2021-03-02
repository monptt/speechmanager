from PyQt5 import QtWidgets
import pyqtgraph as pg
import sys


class MainWindow(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setGeometry(0, 0, 1500, 1500)
        self.initUI()

    def initUI(self):
        graph = graphWindow(self)
        graph.setGeometry(500, 500, 1000, 1000)


class graphWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.graphWidget = pg.PlotWidget(self)
        self.graphWidget.setGeometry(0, 0, 1000, 1000)

        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]

        # plot data: x, y values
        self.graphWidget.plot(hour, temperature)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
