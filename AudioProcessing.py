import time
import numpy as np
from PyQt5.QtCore import QThread, QObject
import mora
import copy

class AudioProcessingClass(QObject):
    def __init__(self, main):
        super().__init__()
        self.mainWindow = main

    def run(self):
        y = np.zeros(10)
        while True:
            moraNum, moraNumPerSec = mora.run()
            time.sleep(0.1)
            y = [*y,moraNumPerSec][1:]
            x = np.arange(len(y))
            print(x)
            print(y)
            self.mainWindow.graph.update(x, y)