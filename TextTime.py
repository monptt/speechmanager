from main import MainWindow
import TextProcessing
import time
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, QObject, pyqtSignal

TEXT_SECOND = 3  # 何秒単位でテキストを操作するか


    
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





