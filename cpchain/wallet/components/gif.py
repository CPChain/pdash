# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout

from cpchain.wallet.simpleqt.decorator import component
from cpchain.wallet.pages import abs_path

class LoadingGif(QWidget):

    def __init__(self, path=None):
        super().__init__()
        self.path = path
        if not path:
            self.path = abs_path('icons/loading.gif')
        self.ui()

    @component.ui
    def ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel('', self)
        movie = QtGui.QMovie(self.path)
        label.setMovie(movie)
        movie.start()
        layout.addWidget(label)
        return layout
