import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plot

import numpy as np
import python_speech_features as psf
import scipy
import scipy.io
import scipy.io.wavfile
import scipy.ndimage
import scipy.signal
import pyaudio
import wave
import time

SECOND = 1

def recording(sec):
    DEVICE_INDEX = 0
    FORMAT = pyaudio.paInt16 # 16bit
    CHANNELS = 1             # monaural
    RATE = 44100             # sampling frequency [Hz]
    CHUNK = RATE * sec

    time = sec # record time [s]       
    output_path = "./sample1.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index = DEVICE_INDEX,
                    frames_per_buffer=CHUNK)

    print("recording ...")

    frames = []

    for i in range(0, int(RATE / CHUNK * time)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("done.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(output_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def getMfcc(fileName):
    (rate, sig) = scipy.io.wavfile.read(fileName)
    mfcc = psf.mfcc(sig, rate)
    delta = psf.delta(mfcc, 2)
    deltaDelta = psf.delta(delta, 2)
    mfccFeature = np.c_[mfcc, delta, deltaDelta]
    return mfccFeature

def getVadFluctuation(mfccPower, deltaPower, filterWidth=10):
    mfccPower[mfccPower < 0] = 0
    deltaPower = np.abs(deltaPower)
    y = mfccPower * deltaPower
    y = scipy.ndimage.gaussian_filter(y, filterWidth)
    minId = scipy.signal.argrelmin(y, order=1)
    minPeek = np.zeros(len(y))
    minPeek[minId] = 1
    maxId = scipy.signal.argrelmax(y, order=1)
    maxPeek = np.zeros(len(y))
    maxPeek[maxId] = 1
    return y, minPeek, maxPeek

def getMoraFlactuation(mfccPower, deltaPower, filterWidth=4):
    y = mfccPower * deltaPower
    y = scipy.ndimage.gaussian_filter(deltaPower, filterWidth)
    minId = scipy.signal.argrelmin(y, order=1)
    minPeek = np.zeros(len(y))
    minPeek[minId] = 1
    maxId = scipy.signal.argrelmax(y, order=1)
    maxPeek = np.zeros(len(y))
    maxPeek[maxId] = 1
    return y, minPeek, maxPeek

def getMoraPerSec(vadSection,moraPositionsNum,sec):
    vadSectionNum = 0
    for i in range(len(vadSection)-1):
        if(vadSection[i+1] > vadSection[i]):
            vadSectionNum += 1
    moraNum = moraPositionsNum + vadSectionNum
    moraNumPerSec = moraNum / sec
    return moraNum, moraNumPerSec

def run():
    recording(SECOND)
    # defines
    vadThreshold = 3

    # MFCC取得
    mfcc = getMfcc("./sample1.wav")
    dataLength = len(mfcc)
    mfccPower = mfcc[:,0]
    deltaPower = mfcc[:,13]

    # Voice active detection
    vad, vadPeekMin, vadPeekMax = getVadFluctuation(mfccPower, deltaPower)

    # mora
    mora, moraPeekMin, moraPeekMax = getMoraFlactuation(mfccPower, deltaPower)

    # voice active detection
    vadSection = np.zeros(dataLength)
    vadSection[vad >= vadThreshold] = 1
    moraPositions = np.zeros(dataLength)
    moraPositions[np.where(moraPeekMax == 1)] = 1
    moraPositions[vad <= vadThreshold] = 0
    sx = np.where(moraPositions == 1)[0]

    moraNum, moraNumPerSec = getMoraPerSec(vadSection,len(sx),SECOND)

    vadThreashold = 2

    return moraNum, moraNumPerSec