import time
import numpy as np
from PyQt5.QtCore import QThread, QObject, pyqtSignal
import mora
import copy
import pyaudio

SECOND = 1 # 何秒ごとに処理するか

DEVICE_INDEX = -1   #default
FORMAT = pyaudio.paInt16 # 16bit
CHANNELS = 1             # monaural
RATE = 16000           # sampling frequency [Hz]
CHUNK = RATE * SECOND


class AudioProcessingClass(QObject):
    updateSignal = pyqtSignal(np.ndarray, np.ndarray)

    def __init__(self, main):
        super().__init__()
        self.mainWindow = main
        self.loopback = False

        ### PyAudioの設定 ###
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        output=True,
                        input_device_index = DEVICE_INDEX,
                        frames_per_buffer=CHUNK)

    def run(self):
        y = np.zeros(10)
        while True:
            frames = self.stream.read(CHUNK)

            if self.loopback==True:
                self.stream.write(frames)   #自分の声を聞く

            # モーラ数カウント
            frames = b''.join([frames])
            sampleBytes = self.p.get_sample_size(FORMAT)

            moraNum, moraNumPerSec = mora.run(RATE, sampleBytes, frames, SECOND)
            #time.sleep(0.1)
            y = np.array([*y,moraNumPerSec][1:])
            x = np.arange(len(y))
            print(x)
            print(y)

            self.updateSignal.emit(x, y)

        # 終了時(このままでは呼ばれない)
        stream.stop_stream()
        stream.close()
        p.terminate()