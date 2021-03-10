from main import MainWindow, nowWindow
import TextProcessing
import time
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, QObject, pyqtSignal, QTimer

TEXT_SECOND = 3  # 何秒単位でテキストを操作するか

class Timer(QtWidgets.QWidget):
    def __init__(self, parent=None, x=0, y=0, w=100, h=100, toUpdate=[]):
        super().__init__(parent)
        self.toUpdate = toUpdate

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
            # タイマーに同期して変更する部分を更新
            for obj in self.toUpdate:
                obj.update(self.t)
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
        for obj in self.toUpdate:
            obj.update(self.t)

    
class textWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QtWidgets.QLabel('<h3>You can upload text</h3>', self)
        self.label2 = QtWidgets.QLabel('<h3>Next Text</h3>', self)
        self.label.setStyleSheet(
            "border-color:blue; border-style:solid; border-width:4px; background-color:red;")
        self.label.setGeometry(0, 0, 500, 50)
        self.label2.setGeometry(0, 100, 500, 50)
        self.mainWindow = parent

        self.rawtextData = []  # ファイルからの形態素解析結果を格納
        self.textList = []  # 読み出し配列を格納
        self.duration = 20 # 全部で何秒で読みたいか
        self.showTime = float(3) # 何秒間以内のテキストを表示するか
        self.nowIndex = 0  # 今どのテキストを見せているか
        self.limitTime = 0 # 今見せているテキストは何秒まで見せるべきか
        self.running = False
    
    def windowInit(self):
        self.mainWindow.movepoint.init_position()
        self.nowIndex = 0
        self.limitTime = self.textList[0]['time']
        self.label.setText(
            f'<h3>{self.textList[0]["text"]}</h3>')
        self.mainWindow.movepoint.w = 12 * \
            len(self.textList[0]["text"])
        self.mainWindow.movepoint.T = self.textList[0]['time']
        if len(self.textList) > 1:
            self.label2.setText(
                f'<h3>{self.textList[1]["text"]}</h3>')
        else:
            self.label2.setText('')

    def update(self, time):
        if len(self.textList) == 0:
            return
        elif time == 0:
            self.windowInit()
            return
        if self.nowIndex == len(self.textList):
            self.label.setText('')
        if time > self.limitTime:
            self.nowIndex += 1
            if self.nowIndex < len(self.textList):
                self.limitTime += self.textList[self.nowIndex]['time']
                self.label.setText(f'<h3>{self.textList[self.nowIndex]["text"]}</h3>')
                if self.nowIndex + 1 < len(self.textList):
                    self.label2.setText(
                        f'<h3>{self.textList[self.nowIndex+1]["text"]}</h3>')
                else:
                    self.label2.setText('')
                self.mainWindow.movepoint.init_position()
                self.mainWindow.movepoint.T = self.textList[self.nowIndex]['time']
                self.mainWindow.movepoint.w = 12 * \
                    len(self.textList[self.nowIndex]["text"])
            else:
                self.label.setText('')
                self.mainWindow.timer.reset()
        else:
            self.label.setText(f'<h3>{self.textList[self.nowIndex]["text"]}</h3>')

    def loadTextFromFile(self, fname):
        # fname[0]は選択したファイルのパス（ファイル名を含む）
        if fname[0]:
            # テキストエディタにファイル内容書き込み
            with open(fname[0], 'r', encoding="utf-8") as f:
                data = f.read()
                # 形態素解析されたテキストのデータ（辞書型）をセット
                self.rawtextData = TextProcessing.makeTextData(data, self.duration)
                self.makeText()
                # 表示を更新
                #self.update(self.textData)
    
    def makeText(self):
        nowTextIndex = 0
        while True:
            timeSum = float(0)
            displayList = []
            brake_flag = False
            while True:
                if timeSum + self.rawtextData[nowTextIndex]['duration'] < self.showTime:
                    displayList.append(self.rawtextData[nowTextIndex])
                    timeSum += self.rawtextData[nowTextIndex]['duration']
                    nowTextIndex += 1
                    if nowTextIndex == len(self.rawtextData):
                        brake_flag = True
                else:
                    break
                if brake_flag:
                    break
            
            # 表示テキストの生成
            displayText = ""
            counter = 0.0
            for textDict in displayList:
                leng = textDict['duration'] / 0.1
                counter += textDict['duration']
                displayText = displayText + textDict['yomi']
                displayText = displayText + ("　"*int(leng))
            displayText += "."
            self.textList.append({"text":displayText, "time":counter})
            if nowTextIndex == len(self.rawtextData):
                break
        self.windowInit()







class TextReplace(QObject):
    updateSignal = pyqtSignal(str)

    def __init__(self, main):
        super().__init__()
        self.mainWindow = main
        self.start = False

    def update(self, time):
        # t=timeのときの表示を記述
        pass

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
                        displayText = displayText + ("　"*int(leng))
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


    def update(self, time):
        # t=timeのときの表示を記述
        pass

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


# 動く点
class movePoint(QtWidgets.QWidget):
    T = 3 # dur 秒間を１周期とする

    def __init__(self, parent=None, x=0, y=0, w=200, h=20):
        super().__init__(parent)
        self.setGeometry(x,y,w,h)
        self.w = w
        self.h = h
        self.pastTime = 0
        self.baseTime = 0
        self.label = QtWidgets.QLabel('<h3>▲</h3>', self)
        self.label.setGeometry(0, 0, w, h)

    def update(self,time:float):
        self.baseTime += (time - self.pastTime)
        self.pastTime = time
        # self.painter.drawRect(10,10,10,10)
        position = int((self.baseTime%self.T)/self.T*self.w)
        # position = int(time /self.T*self.w)
        self.label.setGeometry(position, 0,
                               self.w - position, self.h)

    def init_position(self):
        self.baseTime = 0
        self.label.setGeometry(0, 0, self.w, self.h)

