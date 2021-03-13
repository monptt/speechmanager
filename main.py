from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPainter, QPixmap
import pyqtgraph as pg
import sys
import os

from PyQt5.QtCore import QThread, QObject, pyqtSignal, Qt
from pyqtgraph.functions import disconnect
import AudioProcessing #音声処理用
import TextProcessing # テキスト処理用
import scriptEditor
import thresholdEditor
import TextTime # テキスト表示管理
import numpy as np


def resourcePath(filename):
  if hasattr(sys, "_MEIPASS"):
      return os.path.join(sys._MEIPASS, filename)
  return os.path.join(filename)

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle('Speech Manager 0.0.1')
        self.setGeometry(100, 100, 1000, 1000)
        self.initUI()

        ### 音声処理スレッド　###
        # 外部スレッドからグラフを更新(graph.update(y))する
        self.audioThread = QThread()
        self.audioProcessing = AudioProcessing.AudioProcessingClass(self)
        self.audioProcessing.moveToThread(self.audioThread)

        self.audioThread.started.connect(self.audioProcessing.run)
        self.audioProcessing.updateSignal.connect(self.graph.update)
        self.audioProcessing.updateSignal.connect(self.realtime.update)
        self.audioProcessing.updateSignal_ave.connect(self.average.update)
        self.audioProcessing.updateSignal_ave.connect(self.graph.update_ave)


        # テキスト上のどこを読むべきかを計算
        self.nowposition = TextTime.moveRect(self)

        # 時間計測
        # toUpdate内に入れたウィジェットについて，タイマーに同期して update()が呼ばれる．
        self.timer = TextTime.Timer(self, 0, 0, 300, 100,
            toUpdate=[self.movepoint, self.nowposition, self.textWindow])
        self.timer.move(600,500)

        self.audioThread.start()


    def initUI(self):
        # メニューバーのアイコン設定
        self.openFile = QtWidgets.QAction(QIcon(resourcePath('pictures/computer_folder.png')), 'Open', self)
        self.openScriptEditor = QtWidgets.QAction(QIcon(resourcePath('pictures/word_pro.png')), 'Script Editor', self)
        self.thresholdEditor = QtWidgets.QAction(
            QIcon(resourcePath('pictures/word_pro.png')), 'Threshold Editor', self)
        # ショートカット設定
        self.openFile.setShortcut('Ctrl+O')
        self.openScriptEditor.setShortcut('Ctrl+e')
        self.thresholdEditor.setShortcut('Ctrl+q')
        # ステータスバー設定
        self.openFile.triggered.connect(self.loadTextFromFile)
        self.openScriptEditor.triggered.connect(self.showScriptEditor)
        self.thresholdEditor.triggered.connect(self.showThresholdEditor)


        # メニューバー作成
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openFile)
        fileMenu.addAction(self.openScriptEditor)
        fileMenu.addAction(self.thresholdEditor)

        
        
        self.graph = graphWindow(self)
        self.graph.setGeometry(20, 50, 500, 300)
        self.realtime = nowWindow(self)
        self.realtime.setGeometry(600,20,400,400)
        self.average = averageNum(self)
        self.average.setGeometry(20,500,500,50)
        # 自分の声を聞くかどうか
        self.loopBackCheckBox = QtWidgets.QCheckBox("自分の声を聞く", self)
        def toggleLoopback():
            self.audioProcessing.loopback = not self.audioProcessing.loopback
        self.loopBackCheckBox.stateChanged.connect(toggleLoopback)
        self.loopBackCheckBox.setGeometry(20, 600, 500, 50)
        self.textWindow = TextTime.textWindow(self)
        self.textWindow.setGeometry(20, 700, 800, 250)

        # 動くバー
        self.movepoint = TextTime.movePoint(self, w=800, h=50)
        self.movepoint.setGeometry(20,750,800,50)

    def loadTextFromFile(self):
        # 第二引数はダイアログのタイトル、第三引数は表示するパス
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        self.textWindow.loadTextFromFile(fname)
        self.nowposition.start = True

    def showScriptEditor(self):
        print("Open Script Editor")
        sE = scriptEditor.subWindow(self)
        sE.show()
    
    def showThresholdEditor(self):
        print("Open Threshold Editor")
        sE = thresholdEditor.subWindow(self, self.realtime.normal_threshold, self.realtime.hayai_threshold)
        sE.show()

class graphWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.graphWidget = pg.PlotWidget(self)
        self.graphWidget.setGeometry(0, 0, 500, 300)
        self.graphWidget.setYRange(0,7)

        self.x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.y = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]
        self.initHorizontal = [0]*10

        
        # plot data: x, y values
        self.line = self.graphWidget.plot(self.x, self.y)
        self.horizontal = self.graphWidget.plot(self.x, self.initHorizontal)

    # 描画更新関数
    def update(self, x, y):
        # print("update graph")
        # print(x, y)
        self.line.setData(x,y)
    
    def update_ave(self, newAverage,x):
        # print("update average graph")
        # print(newAverage)
        self.horizontal.setData(x,[newAverage]*len(x))

class averageNum(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.label = QtWidgets.QLabel(f'<h3>average:{0.0}[mora/sec]</h3>', self)
        self.label.setGeometry(0, 0, 500, 50)


    # 描画更新関数
    def update(self, newAverage,x):
        # print("update average")
        # print(newAverage)
        self.label.setText(f'<h3>average:{round(newAverage,3)}[mora/sec]</h3>')

class nowWindow(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.futsuu = QPixmap()
        self.hayai = QPixmap()
        self.osoi = QPixmap()
        self.futsuu.load("pictures/futsuu.png")
        self.hayai.load("pictures/hayai.png")
        self.osoi.load("pictures/osoi.png")
        self.normal_threshold = 2
        self.hayai_threshold = 4

        # plot data: x, y values
        self.lbl = QtWidgets.QLabel(self)
        self.lbl.setGeometry(0, 0, 400, 400)
        self.lbl.setPixmap(self.futsuu)
    
    def update(self, x, y):
        # print("update graph")
        # print(x, y)
        y_3sec = y[len(y)-3:]
        ave_y = np.average(y_3sec)
        if ave_y < self.normal_threshold :
            self.lbl.setPixmap(self.osoi)
        elif ave_y < self.hayai_threshold:
            self.lbl.setPixmap(self.futsuu)
        else:
            self.lbl.setPixmap(self.hayai)
    
    def ch_threshold(self, normal:int, hayai:int):
        self.normal_threshold = normal
        self.hayai_threshold = hayai
        return



def main():
    app = QtWidgets.QApplication(sys.argv)
    


    main = MainWindow()
    main.show()
    sys.exit(app.exec_())





if __name__ == '__main__':
    main()
