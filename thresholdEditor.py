import sys
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, 
    QAction, QFileDialog, QDialog, QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout)
from PyQt5 import QtGui

# テキストフォーム中心の画面のためQMainWindowを継承する
class subWindow:

    def __init__(self, parent=None, normal: int = 2, hayai: int = 4):
        self.w = QDialog(parent)
        self.parent = parent
        self.initUI(normal, hayai)


    def initUI(self, normal, hayai):      
        
        scriptLabel = QLabel()
        scriptLabel.setText('普通の閾値')
        self.script = QLineEdit()
        self.script.setValidator(QtGui.QIntValidator())
        self.script.setText(str(normal))

        secLabel = QLabel()
        secLabel.setText('早いの閾値')
        self.sec = QLineEdit()
        self.sec.setValidator(QtGui.QIntValidator())
        self.sec.setText(str(hayai))

        button = QPushButton('送信')
        button.clicked.connect(self.setParamOriginal)

        layout = QVBoxLayout()
        layout.addWidget(scriptLabel)
        layout.addWidget(self.script)
        layout.addWidget(secLabel)
        layout.addWidget(self.sec)
        layout.addWidget(button)

        self.w.setLayout(layout)


    # ここで親ウィンドウに値を渡している
    def setParamOriginal(self):
        self.parent.realtime.ch_threshold(int(self.script.text()), int(self.sec.text()))

    def show(self):
        self.w.exec_()
