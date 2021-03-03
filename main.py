from PyQt5 import QtWidgets
import pyqtgraph as pg
import sys

from PyQt5.QtCore import QThread, QObject, pyqtSignal
import AudioProcessing #音声処理用

class MainWindow(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setGeometry(100, 100, 800, 500)
        self.initUI()

        ### 音声処理スレッド　###
        # 外部スレッドからグラフを更新(graph.update(y))する
        self.audioThread = QThread()
        self.audioProcessing = AudioProcessing.AudioProcessingClass(self)
        self.audioProcessing.moveToThread(self.audioThread)

        self.audioThread.started.connect(self.audioProcessing.run)
        self.audioProcessing.updateSignal.connect(self.graph.update)

        self.audioThread.start()

    def initUI(self):
        self.graph = graphWindow(self)
        self.graph.setGeometry(20, 20, 500, 300)


class graphWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.graphWidget = pg.PlotWidget(self)
        self.graphWidget.setGeometry(0, 0, 500, 300)

        self.x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.y = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]

        # plot data: x, y values
        self.line = self.graphWidget.plot(self.x, self.y)

    # 描画更新関数
    def update(self, x, y):
        print("update graph")
        print(x, y)
        self.line.setData(x,y)

class nowWindow(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.graphWidget = pg.PlotWidget(self)
        x = [0]
        y = [5]
        self.bg = pg.BarGraphItem(x=x,height=y,width=1,brush='r')
        self.graphWidget.addItem(self.bg)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = nowWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
