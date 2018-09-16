from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget, QRadioButton,
                             QFileDialog, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QCursor, QFont, QFontDatabase, QPainter, QColor, QPen, QPixmap

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

from cpchain import config, root_dir
from cpchain.wallet.pages.personal import Seller

from cpchain.wallet.pages.product import Product2, TableWidget

from cpchain.wallet.pages import app, Binder
from cpchain.wallet.pages.other import PublishDialog

from datetime import datetime as dt

class Product(QWidget):

    def __init__(self, image=None, _id=None, name=None, icon=None, category='category',
                 cpc=0, sales=0, timestamp=None, remain=0, h=135):
        self.image = image
        self.id = _id
        self.name = name
        self.category = category
        self.cpc = cpc
        self.sales = sales
        self.timestamp = timestamp
        self.remain = remain
        self.icon = icon
        self.h = h

        super().__init__()
        self.initUI()

    def initUI(self):
        self.setMaximumWidth(220)
        self.setMaximumHeight(415)

        vbox = QVBoxLayout()
        vbox.addStretch(1)

        # Image
        image = QLabel()
        image.setObjectName('image')
        pixmap = QPixmap(self.image)
        pixmap = pixmap.scaled(220, self.h)
        image.setPixmap(pixmap)

        def listener(event):
            app.router.redirectTo('product_detail', product_id=self.id)

        Binder.click(image, listener)

        vbox.addWidget(image)

        # Name
        name = QLabel(self.name)
        name.setObjectName('name')
        name.setWordWrap(True)
        vbox.addWidget(name)

        # Category
        catbox = QHBoxLayout()
        if self.icon:
            icon = QLabel()
            icon.setMaximumWidth(20)
            icon.setMaximumHeight(20)
            icon.setObjectName('icon')
            icon.setPixmap(QPixmap(self.icon))
            catbox.addWidget(icon)
        category = QLabel(self.category)
        category.setObjectName('category')
        category.setAlignment(Qt.AlignCenter)
        category.setMaximumWidth(52)
        catbox.addWidget(category)
        catbox.addStretch(1)
        vbox.addLayout(catbox)

        # CPC and Sales
        hbox = QHBoxLayout()
        hbox.setObjectName('hbox1')

        cpc = QLabel(str(self.cpc))
        cpc.setObjectName('cpc')
        cpc_unit = QLabel('CPC')
        cpc_unit.setObjectName('cpc_unit')
        sales = QLabel(str(self.sales))
        sales.setObjectName('sales')
        sales_unit = QLabel('sales')
        sales_unit.setObjectName('sales_unit')

        hbox.addWidget(cpc)
        hbox.addWidget(cpc_unit)
        hbox.addWidget(sales)
        hbox.addWidget(sales_unit)
        hbox.addStretch(1)

        vbox.addLayout(hbox)

        # Timestamp and Remain Days
        tbox = QHBoxLayout()
        tmp = self.timestamp
        if not tmp:
            tmp = dt.now()
        months = [
            ["Jan.", "January"],
            ["Feb.", "February"],
            ["Mar.", "March"],
            ["Apr.", "April"],
            ["May", "May"],
            ["Jun.", "June"],
            ["Jul.", "July"],
            ["Aug.", "August"],
            ["Sept.", "September"],
            ["Oct.", "October"],
            ["Nov.", "November"],
            ["Dec.", "December"],
        ]
        tmp_str = months[tmp.month][1] + ' ' + tmp.strftime('%d, %Y')
        timestamp = QLabel(str(tmp_str))
        timestamp.setObjectName('timestamp')
        tbox.addWidget(timestamp)

        if self.remain != None:
            remain = QLabel(str(self.remain) + ' Days Left')
            remain.setObjectName('remain')

        tbox.addWidget(remain)
        tbox.addStretch(1)

        vbox.addLayout(tbox)

        self.setLayout(vbox)
        self.setObjectName('Main')
        # self.setFrameShadow(QFrame.Sunken)



        self.setStyleSheet("""
            #Main {
                background: #ffffff;
                border: 1px solid rgba(0, 0, 0, 0.05);
                border-radius: 5px;
            }
            QLabel {
                font-family:SFUIDisplay-Regular;
            }
            #name {
                font-family:SFUIDisplay-Semibold;
                font-size:14px;
                color:#000000;
                text-align:left;
            }

            #category {
                text-align: center;
                border:1px solid #e9eff5;
                border-radius:3px;
                font-family:SFUIText-Regular;
                font-size:10px;
                color:#3393ed;
                text-align:center;
            }

            #cpc_unit, #sales, #sales_unit{
                font-size:12px;
                color:#999999;
                padding-top: 4px;
            }

            #timestamp {
                font-size:12px;
                color:#999999;
            }

            #cpc {
                font-size:18px;
                color:#000000;
                text-align:left;
            }

            QHBoxLayout#hbox1::hover {
                color:#4a90e2;
            }
        """)
