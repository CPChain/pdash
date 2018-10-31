import importlib
import json
import logging
import os
import os.path as osp
import re
import string
import sys
import traceback
from datetime import datetime as dt

from PyQt5 import QtCore
from PyQt5.QtCore import QObjectCleanupHandler, QPoint, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QCursor, QFont, QFontDatabase
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
                                  get_icon, load_stylesheet, main_wnd, wallet,
                                  warning)
from cpchain.wallet.simpleqt import Signals
from cpchain.wallet.simpleqt.basic import Builder, Button, Input
from cpchain.wallet.simpleqt.decorator import component
from cpchain.wallet.simpleqt.widgets import ComboBox
from cpchain.wallet.simpleqt.widgets.label import Label

logger = logging.getLogger(__name__)

class StreamUploadDialog(Dialog):

    uploaded = pyqtSignal(object)

    def __init__(self, parent=None, oklistener=None):
        width = 400
        height = 280
        title = "Upload Streaming Data"
        self.now_wid = None
        self.oklistener = oklistener
        self.data()
        self.init_proxy()
        super().__init__(wallet.main_wnd, title=title, width=width, height=height)
        self.uploaded.connect(self.uploadedSlot)

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
        self.next_btn = Button.Builder(width=100, height=30).text('Next').click(self.toNext).style('primary').build()
        hbox.addWidget(self.next_btn)

        self.loading = LoadingGif()
        hbox.addWidget(self.loading)
        self.loading.hide()

        layout.addStretch(1)
        layout.addLayout(hbox)
        return layout

    def show_loading(self, flag):
        if flag:
            self.loading.show()
            self.next_btn.hide()
        else:
            self.loading.hide()
            self.next_btn.show()


    def uploadedSlot(self, path):
        self.show_loading(False)
        result = StreamUploadedDialog(oklistener=self.oklistener, data_name=self.data_name.value, stream_id=path['ws_url'])
        result.show()
        self.close()

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
                self.uploaded.emit(path)
            except Exception as err:
                logger.error(err)
        self.show_loading(True)
        self.upload().addCallbacks(callback)

    @component.method
    def upload(self):
        proxy = self.proxy.current
        storage_type = 'stream'
        storage_plugin = "cpchain.storage_plugin."
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
