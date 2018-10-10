# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QFrame

from cpchain.wallet.simpleqt.decorator import component
from cpchain.wallet.pages import abs_path

class LoadingGif(QFrame):

    def __init__(self, parent=None, path=None, width=20, height=20):
        super().__init__(parent)
        self.path = path
        self.width_ = width
        self.height_ = height
        self.setObjectName('loading')
        if not path:
            self.path = abs_path('icons/loading.gif')
        self.ui()

    @component.ui
    def ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel('', self)
        movie = QtGui.QMovie(self.path)
        movie.setCacheMode(QtGui.QMovie.CacheAll)
        movie.setSpeed(80)
        movie.setScaledSize(QSize(self.width_, self.height_))
        label.setMovie(movie)
        movie.start()
        layout.addWidget(label)
        self.setContentsMargins(0, 0, 0, 0)
        return layout
