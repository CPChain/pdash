# -*- coding: utf-8 -*-
import os
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import  QPixmap

from cpchain.wallet.simpleqt.decorator import component
from cpchain.wallet.components.gif import LoadingGif
from cpchain.wallet.pages import wallet

class Picture(QWidget):

    loaded = pyqtSignal(object)

    def __init__(self, path=None, width=None, height=None):
        super().__init__()
        self.path = path
        self.width = width
        self.height = height
        self.loaded.connect(self.loadedSlot)
        self.ui()

    def loadedSlot(self, content):
        photo = QPixmap()
        photo.loadFromData(content)
        photo = photo.scaled(self.width, self.height)
        self.gif.deleteLater()
        label = QLabel()
        label.setPixmap(photo)
        self.layout.addWidget(label)

    @component.method
    def get_picture(self):
        def cb(content):
            self.loaded.emit(content)
        wallet.market_client.get('product/v1/allproducts/images/?path=' + self.path, True).addCallbacks(cb)

    @component.ui
    def ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        if os.path.exists(self.path):
            photo = QPixmap(self.path)
            #photo.loadFromData(req.content, "JPG")
            # photo.loadFromData(req.content)
            photo = photo.scaled(self.width, self.height)

            label = QLabel()
            label.setPixmap(photo)
            self.photo = photo
            layout.addWidget(label)
        else:
            self.get_picture()
            gif = LoadingGif()
            self.gif = gif
            layout.addWidget(gif)
        self.layout = layout
        return layout
