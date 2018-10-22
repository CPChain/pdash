import importlib
import json
import logging
import os
import os.path as osp
import random
import re
import string
import sys
import time
import traceback
from datetime import datetime as dt

from PyQt5 import QtCore
from PyQt5.QtCore import (QObject, QObjectCleanupHandler, QPoint, Qt, QThread,
                          QUrl, pyqtProperty, pyqtSignal, pyqtSlot)
from PyQt5.QtGui import QCursor, QFont, QFontDatabase
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication,
                             QCheckBox, QComboBox, QDialog, QFileDialog,
                             QFrame, QGridLayout, QHBoxLayout, QHeaderView,
                             QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QMenu, QMessageBox, QPushButton, QRadioButton,
                             QScrollArea, QTableWidget, QTableWidgetItem,
                             QTabWidget, QTextEdit, QVBoxLayout, QWidget)
from sqlalchemy import func
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from twisted.python import log

from autobahn.twisted.websocket import (WebSocketClientFactory,
                                        WebSocketClientProtocol, connectWS)
from cpchain import root_dir
from cpchain.crypto import AESCipher, ECCipher, Encoder, RSACipher
from cpchain.proxy.client import pick_proxy
from cpchain.utils import open_file, sizeof_fmt
from cpchain.wallet import fs
from cpchain.wallet.components.dialog import Dialog
from cpchain.wallet.components.gif import LoadingGif
from cpchain.wallet.db import FileInfo
from cpchain.wallet.pages import (Binder, HorizontalLine, abs_path, app,
                                  get_icon, load_stylesheet, main_wnd,
                                  qml_path, wallet, warning)
from cpchain.wallet.simpleqt import Signals
from cpchain.wallet.simpleqt.basic import Builder, Button, Input
from cpchain.wallet.simpleqt.component import Component
from cpchain.wallet.simpleqt.decorator import component
from cpchain.wallet.simpleqt.widgets import ComboBox
from cpchain.wallet.simpleqt.widgets.label import Label

logger = logging.getLogger(__name__)


class MyClientProtocol(WebSocketClientProtocol):

    def onMessage(self, payload, isBinary):
        if isBinary:
            pass
        else:
            self.factory.handler(payload.decode('utf8'))


class PreviewObject(QObject):

    tickComing = pyqtSignal(str, arguments=["tick"])

    def __init__(self, parent=None):
        super().__init__(parent)
        # deferToThread(self.test)

    def test(self):
        while True:
            ts = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            temperature = random.randint(20, 25)
            huminity = random.randint(28, 35)
            self.tickComing.emit(
                "{} temperature:{} huminity:{}".format(ts, temperature, huminity))
            time.sleep(1)


class PreviewWidget(Component):

    qml = qml_path('components/Preview.qml')

    def __init__(self, parent=None):
        self.obj = PreviewObject(parent)
        super().__init__(parent)

    @component.create
    def create(self):
        pass

    @component.ui
    def ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        widget = QQuickWidget(self)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.rootContext().setContextProperty('self', self.obj)
        widget.setSource(QUrl(self.qml))
        layout.addWidget(widget)
        return layout


class PreviewDialog(Dialog):

    def __init__(self, parent=None, oklistener=None, ws_url=None):
        width = 700
        height = 550
        title = "Preview"
        self.ws_url = ws_url
        self.now_wid = None
        self.oklistener = oklistener
        self.data()
        self.signals = Signals()
        super().__init__(wallet.main_wnd, title=title, width=width, height=height)
        self.signals.change.connect(self.modelChange)
        self.stream.setView(self)

        self.run_client(self.ws_url)

    def run_client(self, ws_url):
        self.factory = WebSocketClientFactory(ws_url + '?action=subscribe')
        self.factory.protocol = MyClientProtocol

        def handler(record):
            self.stream.append(record)
        self.factory.handler = handler
        connectWS(self.factory)

    def close(self):
        super().close()

    def modelChange(self, val):
        # data = Builder().name('ts').text(str(val)).build()
        # self._layout.insertLayout(0, self.row(data))
        print(val)
        self.obj.tickComing.emit(val)

    @component.data
    def data(self):
        return {
            "stream": [

            ]
        }

    def row(self, data):
        layout = QHBoxLayout()
        layout.addWidget(data)
        return layout

    def ui(self, widget):
        self.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)
        datas = self.stream.value

        for i in datas:
            data = Builder().name('ts').text(str(i)).build()
            layout.insertLayout(0, self.row(data))
        self._layout = layout
        wid = QFrame()
        wid.setLayout(layout)
        wid.setContentsMargins(0, 0, 0, 0)
        wid.setStyleSheet("""
            QFrame {
                background: #fff;
            }
            QWidget#ts {
                border: none;
            }
            QLabel#header {
                border: 1px solid black;
            }

        """)

        scroll = QScrollArea()
        scroll.setContentsMargins(0, 0, 0, 0)
        scroll.setWidgetResizable(True)

        # scroll.setWidget(wid)
        preview = PreviewWidget()
        self.obj = preview.obj
        scroll.setWidget(preview)

        _main = QVBoxLayout()

        _main.addWidget(Builder().text('Stream ID:').build())
        _main.addWidget(Builder().text(self.ws_url).build())

        _main.addWidget(scroll)

        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignRight)
        hbox.addWidget(Button.Builder(width=100, height=30).text(
            'OK').click(lambda _: self.close()).build())
        _main.addLayout(hbox)
        return _main

    def style(self):
        return super().style() + """
        QLabel#header {
            border: 1px solid black;
        }
        QScrollArea {
            background: #fff;
            /*border: 1px solid #666;*/
        }
        """
