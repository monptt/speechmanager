from main import MainWindow
import time
from PyQt5.QtCore import QThread, QObject, pyqtSignal

TEXT_SECOND = 3  # 何秒単位でテキストを操作するか


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
                print("------text data approved ----")
                while self.start:
                    timeSum = 0
                    displayList = []
                    # TEXT_SECOND内に収まるテキストを取得
                    while True:
                        if timeSum + textData[nowTextIndex]['duration'] < TEXT_SECOND:
                            displayList.append(textData[nowTextIndex])
                            timeSum += textData[nowTextIndex]['duration']
                            nowTextIndex += 1
                        else:
                            break
                    
                    # 表示テキストの生成
                    displayText = ""
                    for textDict in displayList:
                        leng = textDict['duration'] / 0.1
                        displayText = displayText + textDict['text']
                        displayText = displayText + (" "*int(leng))
                    print(displayText)
                    self.updateSignal.emit(displayText)
                    time.sleep(TEXT_SECOND)
                






