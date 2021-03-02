import time
import numpy as np
from PyQt5.QtCore import QThread, QObject

class AudioProcessingClass(QObject):
    def __init__(self, main):
        super().__init__()
        self.mainWindow = main

    def run(self):
        while True:
            # 0.5秒ごとに，ランダムな10個の値でグラフを更新する
            time.sleep(0.5)
            x = np.arange(10)
            y = np.random.rand(10)
            self.mainWindow.graph.update(x, y)