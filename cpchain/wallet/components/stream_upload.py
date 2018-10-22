from PyQt5.QtCore import Qt, QPoint, QObjectCleanupHandler, QThread
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget, QRadioButton,
                             QFileDialog, QListWidget, QListWidgetItem, QComboBox)
from PyQt5.QtGui import QCursor, QFont, QFontDatabase

from cpchain.crypto import ECCipher, RSACipher, Encoder

from cpchain.wallet.pages import load_stylesheet, HorizontalLine, wallet, main_wnd, app

from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from cpchain.wallet import fs
from cpchain.crypto import AESCipher
from cpchain.utils import open_file, sizeof_fmt
from cpchain.proxy.client import pick_proxy

import importlib
import os
import os.path as osp
import string
import logging
import re
import traceback
import json
import sys
from sqlalchemy import func

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory, connectWS
from twisted.internet.threads import deferToThread
from twisted.python import log

from cpchain import root_dir

from cpchain.wallet.db import FileInfo
from cpchain.wallet.pages import main_wnd, HorizontalLine, abs_path, get_icon, Binder, warning, wallet
from cpchain.wallet.components.dialog import Dialog
from cpchain.wallet.simpleqt.decorator import component
from cpchain.wallet.simpleqt.widgets import ComboBox
from cpchain.wallet.simpleqt.widgets.label import Label
from cpchain.wallet.components.gif import LoadingGif

from cpchain.wallet.simpleqt.basic import Builder, Input, Button
from cpchain.wallet.simpleqt import Signals

from datetime import datetime as dt

logger = logging.getLogger(__name__)

class StreamUploadDialog(Dialog):
    def __init__(self, parent=None, oklistener=None):
        width = 400
        height = 280
        title = "Upload Streaming Data"
        self.now_wid = None
        self.oklistener = oklistener
        self.data()
        self.init_proxy()
        super().__init__(wallet.main_wnd, title=title, width=width, height=height)

    @component.method
    def init_proxy(self):
        def set_proxy(proxy):
            self.proxy.value = proxy
        pick_proxy().addCallbacks(set_proxy)

    @component.data
    def data(self):
        return {
            "data_name": "",
            "proxy": []
        }

    def ui(self, widget):
        layout = QVBoxLayout(widget)
        width = 340
        layout.addWidget(Builder().name('field').text('Data name:').build())
        layout.addWidget(Input.Builder(width=width).model(self.data_name).name('data-name').placeholder('Please input data name').build())
        layout.addSpacing(10)
        layout.addWidget(Builder().name('field').text('Select a Proxy:').build())

        combox = ComboBox(self.proxy)
        combox.setMaximumWidth(width + 24)
        combox.setMinimumWidth(width + 24)
        layout.addWidget(combox)

        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignRight)
        hbox.addWidget(Button.Builder(width=100, height=30).text('Cancel').click(lambda _: self.close()).build())
        hbox.addSpacing(10)
        hbox.addWidget(Button.Builder(width=100, height=30).text('Next').click(self.toNext).style('primary').build())

        layout.addStretch(1)
        layout.addLayout(hbox)
        return layout
    
    def toNext(self, _):
        # Upload to proxy, get streaming id
        def callback(path):
            try:
                # Save
                proxy = self.proxy.current
                self.aes_key = AESCipher.generate_key()
                remote_uri = str(path)
                new_file_info = FileInfo(name=self.data_name.value, data_type='stream', proxy=proxy,
                                        remote_type='stream', remote_uri=remote_uri, public_key=wallet.market_client.public_key,
                                        is_published=False, created=func.current_timestamp(), aes_key=self.aes_key)
                fs.add_file(new_file_info)
                self._id = new_file_info.id
                encrypted_key = RSACipher.encrypt(self.aes_key)
                encrypted_key = Encoder.bytes_to_base64_str(encrypted_key)
                wallet.market_client.upload_file_info(None, None, 0, self._id, 'stream', json.dumps(remote_uri), self.data_name.value, encrypted_key)
                path = json.loads(path)
                result = StreamUploadedDialog(oklistener=self.oklistener, data_name=self.data_name.value, stream_id=path['ws_url'])
                result.show()
                self.close()
            except Exception as err:
                logger.error(err)
        self.upload().addCallbacks(callback)
    
    @component.method
    def upload(self):
        proxy = self.proxy.current
        storage_type = 'stream'
        storage_plugin = "cpchain.storage-plugin."
        module = importlib.import_module(storage_plugin + storage_type)
        s = module.Storage()
        param = dict()
        param['proxy_id'] = proxy # should be selected by UI from proxy list
        path = s.upload_data(None, param)
        return path

    def style(self):
        return super().style() + """
        QLabel#field {
            font-size: 16px;
        }
        """

class StreamUploadedDialog(Dialog):
    
    def __init__(self, parent=None, oklistener=None, data_name=None, stream_id=None):
        width = 400
        height = 340
        title = "Streaming ID"
        self.now_wid = None
        self.oklistener = oklistener
        self.data_name_ = data_name
        self.stream_id_ = stream_id
        self.data()
        super().__init__(wallet.main_wnd, title=title, width=width, height=height)


    @component.data
    def data(self):
        return {
            "data_name": self.data_name_,
            "stream_id": self.stream_id_
        }
    
    def copyText(self, _):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.stream_id.value)

    def close(self):
        if self.oklistener:
            self.oklistener()
        super().close()

    def ui(self, widget):
        layout = QVBoxLayout(widget)
        width = 300
        layout.addWidget(Builder().name('field').text('Data name:').build())
        layout.addWidget(Builder(Label).name('value').text(self.data_name.value).wrap(True).model(self.data_name).build())
        layout.addSpacing(10)
    
        layout.addWidget(Builder().name('field').text('Stream ID:').build())
        layout.addWidget(Builder(Label).name('value').text(self.stream_id.value).wrap(True).model(self.stream_id).build())
        layout.addSpacing(10)

        layout.addWidget(Builder().name('copy').text('copy').click(self.copyText).build())

        layout.addStretch(1)
        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignRight)
        hbox.addWidget(Button.Builder(width=100, height=30).text('OK').click(lambda _: self.close()).build())
        layout.addLayout(hbox)
        return layout

    def style(self):
        return super().style() + """
        QLabel#field {
            font-size: 16px;
        }
        QLabel#value {
            font-size: 13px;
            margin-top: 5px;
        }
        QLabel#copy {
            color: #1689e9;
            margin-left: 5px;
        }
        """
