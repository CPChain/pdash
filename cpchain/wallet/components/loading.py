from PyQt5.QtWidgets import (QLabel, QHBoxLayout, QWidget, QFrame)
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtCore import Qt, QSize
from cpchain.wallet.pages import abs_path

from cpchain.wallet.components.gif import LoadingGif

class Loading(QFrame):
    def __init__(self, parent=None, text="processing..."):
        self.text_ = text
        super().__init__(parent)
        self.setObjectName('Loading')
        self.initUI()

    def initUI(self):
        self.setObjectName('Loading')
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)
        loading = LoadingGif(self, path=abs_path('icons/new_loading.gif'))
        loading.setObjectName('loading')
        layout.addWidget(loading)
        text = QLabel(self.text_)
        text.setObjectName('Text')
        text.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(text)
        self.setStyleSheet("""
        QLabel#Text {
            font-family:SFUIDisplay-Semibold;
            font-size: 14px;
            color: #9B9B9B;
            padding-bottom: 3px;
            padding-left: 3px;
        }
        QFrame#Loading {
        }
        QFrame#loading {
        }
        """)
        self.setLayout(layout)
        self.setContentsMargins(0, 0, 0, 0)
