from PyQt5.QtWidgets import QLabel, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt
from cpchain.wallet.pages import abs_path

from cpchain.wallet.components.gif import LoadingGif

class Loading(QFrame):
    def __init__(self, parent=None, text="processing...", font_size=14, width=20, height=20):
        self.text_ = text
        self.width_ = width
        self.font_size = font_size
        self.height_ = height
        super().__init__(parent)
        self.setObjectName('Loading')
        self.initUI()

    def initUI(self):
        self.setObjectName('Loading')
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)
        loading = LoadingGif(self, path=abs_path('icons/new_loading.gif'), width=self.width_, height=self.height_)
        loading.setObjectName('loading')
        layout.addWidget(loading)
        text = QLabel(self.text_)
        text.setObjectName('Text')
        text.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(text)
        self.setStyleSheet("""
        QLabel#Text {{
            font-size: {}px;
            color: #9B9B9B;
            padding-bottom: 3px;
            padding-left: 3px;
        }}
        """.format(self.font_size))
        self.setLayout(layout)
        self.setContentsMargins(0, 0, 0, 0)
