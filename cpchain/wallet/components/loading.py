from PyQt5.QtWidgets import (QLabel, QVBoxLayout, QDialog)
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtCore import Qt, QSize
from cpchain.wallet.pages import abs_path

from cpchain.wallet.components.gif import LoadingGif

class Loading(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(250, 220)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        image = QLabel()
        image.setObjectName('image')
        path = abs_path('icons/loading.png')
        pix = QPixmap(path)
        width = 100
        height = 100
        image.resize(width, height)
        pix.scaled(QSize(width, height), Qt.KeepAspectRatio)
        image.setPixmap(pix)

        # gif = QMovie(abs_path('icons/animat-network-color.gif'))
        # image.setMovie(gif)
        # gif.start()

        layout.addWidget(image)
        self.setLayout(layout)
