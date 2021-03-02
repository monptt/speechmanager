import time
import numpy as np
from PyQt5.QtCore import QThread, QObject
import mora

class AudioProcessingClass(QObject):
    def __init__(self, main):
        super().__init__()
        self.mainWindow = main

    def run(self):
        y = np.zeros(10)
        while True:
            moraNum, moraNumPerSec = mora.run()
            print(moraNum)
            print(moraNumPerSec)
            y = np.append(y,moraNumPerSec)
            y = np.delete(y,0)
            x = np.arange(len(y))
            print(x)
            print(y)
            self.mainWindow.graph.update(x, y)
            self.mainWindow.show()