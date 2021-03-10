import sys
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, 
    QAction, QFileDialog, QDialog, QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout)
from PyQt5.QtGui import QIcon

# テキストフォーム中心の画面のためQMainWindowを継承する
class subWindow:

    def __init__(self, parent=None):
        self.w = QDialog(parent)
        self.parent = parent
        self.initUI()


    def initUI(self):      
        
        scriptLabel = QLabel()
        scriptLabel.setText('Input script here')
        self.script = QTextEdit()

        secLabel = QLabel()
        secLabel.setText('Input sec here')
        self.sec = QLineEdit()
        

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
        print("setParamOriginal")
        self.parent.textWindow.makeTextDataFromInput(self.script.toPlainText(),int(self.sec.text()))

    def show(self):
        self.w.exec_()