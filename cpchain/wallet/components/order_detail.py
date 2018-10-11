from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget, QRadioButton,
                             QFileDialog, QListWidget, QListWidgetItem, QComboBox)
from PyQt5.QtGui import QCursor, QFont, QFontDatabase, QPixmap
from PyQt5 import QtGui

from cpchain.crypto import ECCipher, RSACipher, Encoder

from cpchain.wallet.pages import load_stylesheet, HorizontalLine, wallet, main_wnd, get_pixm

from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from cpchain.wallet import fs
from cpchain.utils import open_file, sizeof_fmt
from cpchain.proxy.client import pick_proxy

import importlib
import os
import os.path as osp
import string
import logging
import json
import shutil

from cpchain import root_dir

from cpchain.wallet.utils import formatTimestamp
from cpchain.wallet.pages import HorizontalLine, abs_path, get_icon, app, Binder, wallet
from cpchain.wallet.pages.other import PublishDialog

from cpchain.wallet.components.table import Table
from cpchain.wallet.components.product import Product
from cpchain.wallet.components.product_list import ProductList
from cpchain.wallet.components.upload import UploadDialog
from cpchain.wallet.components.loading import Loading
from cpchain.wallet.components.sales import Sale
from cpchain.wallet.components.purchase import PurchaseDialog
from cpchain.wallet.components.picture import Picture

from cpchain.wallet.simpleqt.page import Page
from cpchain.wallet.simpleqt.decorator import page
from cpchain.wallet.simpleqt.widgets.label import Label
from cpchain.wallet.simpleqt.widgets import Input
from cpchain.wallet.simpleqt.model import Model

from cpchain.wallet.components.sales import Operator

from cpchain.wallet.components.stream_upload import StreamUploadedDialog, PreviewDialog

from datetime import datetime as dt

logger = logging.getLogger(__name__)

class OrderDetail(QWidget):

    def __init__(self, order_time, status, order_id, name=None, storage_path=None, data_type='batch',
                 stream_id=None, market_hash=None):
        self.order_time = order_time
        self.status = status
        self.order_id = order_id
        self.operator = Operator()
        self.storage_path = storage_path
        self.data_type = data_type
        self.market_hash = market_hash
        self.name = name
        self.stream_id = stream_id
        super().__init__()
        self.ui()

    def gen_row(self, name, widget):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        nameWid = QLabel(name)
        nameWid.setMinimumWidth(100)
        nameWid.setObjectName("order_item_name")
        layout.addWidget(nameWid)
        layout.addWidget(widget)
        if isinstance(widget, Label):
            widget.setObjectName('order_item_value')
        tmp = QWidget()
        tmp.setLayout(layout)
        tmp.setObjectName('order_item')
        return tmp

    def select_storage_path(self, _=None):
        self.storage_path = QFileDialog.getExistingDirectory()

    def download(self):
        order_info = wallet.chain_broker.buyer.query_order(self.order_id)
        # Select Storage Path
        if self.storage_path is None:
            self.select_storage_path()
        # Download
        path = fs.buyer_file_by_order_id(self.order_id).path
        new_path = self.storage_path + '/' + self.name
        shutil.copyfile(path, new_path)

    def confirm(self):
        self.operator.buyer_confirm(self.order_id)

    def ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.gen_row('Order Time:', Label(self.order_time)))
        layout.addWidget(self.gen_row('Staus:', Label(self.status)))

        # Bottom
        btm = QHBoxLayout()
        btm.setAlignment(Qt.AlignLeft)
        btm.setContentsMargins(0, 0, 0, 0)
        btm.setSpacing(15)


        if self.data_type == 'batch':
            ok = QPushButton('Download')
            ok.setObjectName('pinfo_publish_btn')
            btm.addWidget(ok)
            ok.clicked.connect(self.download)
            cancel = QPushButton('Confirm')
            cancel.setObjectName('pinfo_cancel_btn')
            cancel.clicked.connect(self.confirm)
            btm.addWidget(cancel)
            btm.addStretch(1)
            layout.addLayout(btm)

            storage = QLabel('Open Storage Path…')
            storage.setStyleSheet("""
                margin-top: 12px;
                font-family:SFUIDisplay-Medium;
                font-size:14px;
                color:#0073df;
            """)
            Binder.click(storage, self.select_storage_path)
            layout.addWidget(storage)
        else:
            ok = QPushButton('Get Streaming ID')
            ok.setObjectName('pinfo_stream_btn')
            def openStreamID(_):
                def cb(path):
                    if path:
                        stream_id = json.loads(path)
                        dlg = StreamUploadedDialog(data_name=self.name, stream_id=stream_id[0])
                        dlg.show()
                deferToThread(lambda: fs.buyer_file_by_order_id(self.order_id).path).addCallback(cb)
            ok.clicked.connect(openStreamID)
            btm.addWidget(ok)
            preview = QPushButton('Preview')
            preview.setObjectName('pinfo_cancel_btn')
            def openPreview(_):
                dlg = PreviewDialog()
                dlg.show()
            preview.clicked.connect(openPreview)
            btm.addWidget(preview)
            confirm = QPushButton('Confirm')
            confirm.setObjectName('pinfo_cancel_btn')
            btm.addWidget(confirm)
            btm.addStretch(1)
            layout.addLayout(btm)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget#order_item {
                margin-top: 20px;
                margin-bottom: 20px;
            }
            QLabel#order_item_name {
                font-family:SFUIDisplay-Regular;
                font-size:14px;
                color:#666666;
                text-align:left;
            }
            Label#order_item_value {
                font-family:SFUIDisplay-Regular;
                font-size:14px;
                color:#000000;
                text-align:left;
            }
            QPushButton#pinfo_cancel_btn{
                padding-left: 10px;
                padding-right: 10px;
                border: 1px solid #3173d8; 
                border-radius: 3px;
                color: #3173d8;
                min-height: 30px;
                max-height: 30px;
                background: #ffffff;
                min-width: 80px;
                max-width: 80px;
            }

            QPushButton#pinfo_cancel_btn:hover{
                border: 1px solid #3984f7; 
                color: #3984f6;
            }

            QPushButton#pinfo_cancel_btn:pressed{
                border: 1px solid #2e6dcd; 
                color: #2e6dcd;
                background: #e5ecf4;
            }

            QPushbutton#pinfo_cancel_btn:disabled{
                border: 1px solid #8cb8ea; 
                color: #8cb8ea;
            }

            QPushButton#pinfo_publish_btn, QPushButton#pinfo_stream_btn{
                padding-left: 10px;
                padding-right: 10px;
                border: 1px solid #3173d8; 
                border-radius: 3px;
                color: #ffffff;
                min-height: 30px;
                max-height: 30px;
                min-width: 80px;
                max-width: 80px;
                background: #3173d8;
            }

            QPushButton#pinfo_publish_btn:hover, QPushButton#pinfo_stream_btn:hover{
                background: #3984f7; 
                border: 1px solid #3984f7;
            }

            QPushButton#pinfo_publish_btn:pressed, QPushButton#pinfo_stream_btn:pressed{
                border: 1px solid #2e6dcd; 
                background: #2e6dcd;
            }

            QPushbutton#pinfo_publish_btn:disabled, QPushButton#pinfo_stream_btn:disabled{
                border: 1px solid #8cb8ea; 
                background: #98b9eb;
            }

            QPushButton#pinfo_stream_btn {
                min-width: 120px;
                max-width: 120px;
            }
        """)
