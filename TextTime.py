from main import MainWindow
import TextProcessing
import time
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, QObject, pyqtSignal, QTimer

TEXT_SECOND = 3  # 何秒単位でテキストを操作するか

class Timer(QtWidgets.QWidget):
    def __init__(self, parent=None, x=0, y=0, w=100, h=100):
        super().__init__(parent)
        # 時間処理変数
        self.t = 0
        self.running = False

        # タイマー（内部処理用）
        self.qtimer = QTimer(self)
        self.qtimer.timeout.connect(self.update)
        self.qtimer.start(10)

        ### 時間表示用 GUI パーツ ###
        self.mainWindow = parent
        self.setGeometry(x, y, w, h)

        self.label = QtWidgets.QLabel(str(self.t), self)
        self.label.setGeometry(0, 0, w, h*0.5)
        self.label.setStyleSheet(
            "border: solid 1px black; background-color:#ffffff;")

        self.startBtn = QtWidgets.QPushButton("Start", self)
        self.startBtn.setGeometry(0, h*0.5, w*0.5, h*0.5)
        self.startBtn.clicked.connect(self.start)

        self.resetBtn = QtWidgets.QPushButton("Reset", self)
        self.resetBtn.setGeometry(w*0.5, h*0.5, w*0.5, h*0.5)
        self.resetBtn.clicked.connect(self.reset)

    def update(self):
        if(self.running):
            self.t += 0.01
        else:
            pass
        self.label.setText(str(self.t))
    
    def start(self):
        print("timer start")
        self.running = True

    def reset(self):
        print("timer reset")
        self.t = 0
        self.running = False

    
class textWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QtWidgets.QLabel('<h3>You can upload text</h3>', self)
        self.label.setStyleSheet(
            "border-color:blue; border-style:solid; border-width:4px; background-color:red;")
        self.label.setGeometry(0, 0, 500, 50)
        self.mainWindow = parent
        
        self.textData = {}
        self.duration = 20 # 全部で何秒で読みたいか

        self.running = False

    def update(self, newTextData):
        # テキスト（辞書型）を受け取り，表示
        # print("update text")
        # self.textData = newTextData
        # print(newTextData)
        # self.label.setText(f'<h3>{newTextData}</h3>')
        if newTextData != "|":
            self.label.setText(newTextData)
        else:
            self.label.setText("")
            self.mainWindow.textTime.start = False
            self.mainWindow.nowposition.start = False
            self.mainWindow.movepoint.init_position()

        print("-------mojisuu-------"+str(len(newTextData)))

    def loadTextFromFile(self, fname):
        # fname[0]は選択したファイルのパス（ファイル名を含む）
        if fname[0]:
            # テキストエディタにファイル内容書き込み
            with open(fname[0], 'r', encoding="utf-8") as f:
                data = f.read()
                # 形態素解析されたテキストのデータ（辞書型）をセット
                self.textData = TextProcessing.makeTextData(data, self.duration)
                print(self.textData)
                # 表示を更新
                #self.update(self.textData)

class TextReplace(QObject):
    updateSignal = pyqtSignal(str)

    def __init__(self, main):
        super().__init__()
        self.mainWindow = main
        self.start = False

    def run(self):
        while True:
            if self.mainWindow.text.textData:
                textData = self.mainWindow.text.textData 
                nowTextIndex = 0
                brake_flag = False
                while self.start:
                    timeSum = 0
                    displayList = []
                    # TEXT_SECOND内に収まるテキストを取得
                    while True:
                        if brake_flag:
                            break
                        if timeSum + textData[nowTextIndex]['duration'] < TEXT_SECOND:
                            displayList.append(textData[nowTextIndex])
                            timeSum += textData[nowTextIndex]['duration']
                            nowTextIndex += 1
                            if nowTextIndex == len(textData):
                                brake_flag = True
                        else:
                            break
                    
                    # 表示テキストの生成
                    displayText = ""
                    for textDict in displayList:
                        leng = textDict['duration'] / 0.1
                        displayText = displayText + textDict['text']
                        displayText = displayText + (" "*int(leng))
                    if brake_flag and displayText=="":
                        displayText="|"
                    print(displayText)
                    self.updateSignal.emit(displayText)
                    time.sleep(TEXT_SECOND)
                

class moveRect(QObject):
    updateSignal = pyqtSignal(float)
    def __init__(self, main):
        super().__init__()
        self.mainWindow = main
        self.start = False
        self.unittime = 0.1

    def run(self):
        while True:
            if self.mainWindow.text.textData:
                now_time:float = 0
                while self.start:
                    self.updateSignal.emit(now_time)
                    now_time += self.unittime
                    time.sleep(self.unittime)
                    if now_time > TEXT_SECOND:
                        now_time = 0
                    print("----in the move thread------"+str(now_time))



class movePoint(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.label = QtWidgets.QLabel('<h3>.</h3>', self)
        self.label.setGeometry(0, 0, 500, 50)
    def update(self,time:float):
        # self.painter.drawRect(10,10,10,10)
        print("------debug----time-------"+str(time))
        self.label.setGeometry(int(float(500/3)*time), 0,
                               500-int(float(500/3)*time), 50)
    def init_position(self):
        self.label.setGeometry(0, 0, 500, 50)

