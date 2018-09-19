# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QLabel, QWidget, QMovie

class loadingGif(QWidget):

    def __init__(self, parent=None):
        super(loadingGif, self).__init__(parent)
        self.label = QLabel('', self)
        self.setFixedSize(200, 200)
        self.setWindowFlags(QtCore.Qt.Dialog|QtCore.Qt.CustomizeWindowHint)
        self.movie = QtGui.QMovie("loading.gif")
        self.label.setMovie(self.movie)
        self.movie.start()
