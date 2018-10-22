from PyQt5.QtCore import Qt, QPoint, QObject, pyqtSlot, pyqtSignal, pyqtProperty, QUrl
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget, QRadioButton,
                             QFileDialog, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QCursor, QFont, QFontDatabase, QPainter, QColor, QPen, QPixmap
from PyQt5.QtQuickWidgets import QQuickWidget

from cpchain.crypto import ECCipher, RSACipher, Encoder

from cpchain.wallet.pages import load_stylesheet, HorizontalLine, wallet, main_wnd, get_pixm, qml_path

from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from cpchain.wallet import fs
from cpchain.utils import open_file, sizeof_fmt

import importlib
import os
import os.path as osp
import string
import logging

from cpchain import config, root_dir
from cpchain.wallet.pages import app, Binder
from cpchain.wallet.components.picture import Picture
from cpchain.wallet.simpleqt.component import Component
from cpchain.wallet.simpleqt.decorator import component

from datetime import datetime as dt

from . import ProductObject, ImageObject


class ProductQML(Component):

    qml = qml_path('components/Product.qml')

    def __init__(self, parent, image=None, img_width=None, img_height=None, market_hash=None):
        self.obj = ImageObject(None, image, img_width,
                               img_height, market_hash=market_hash)
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


class Product(QWidget):

    def __init__(self, image=None, _id=None, name=None, icon=None, category='category',
                 cpc=0, sales=0, timestamp=None, remain=0, description="", market_hash=None, h=135,
                 owner_address=None, ptype=None):
        self.image = image
        self.id = _id
        self.name = name
        self.category = category
        self.cpc = cpc
        self.sales = sales
        self.timestamp = timestamp
        self.remain = remain
        self.icon = icon
        self.description = description
        self.h = h
        self.market_hash = market_hash
        self.ptype = ptype
        self.owner_address = owner_address

        super().__init__()
        self.initUI()

    def initUI(self):
        self.setMaximumWidth(220)
        self.setMaximumHeight(415)

        vbox = QVBoxLayout()
        # vbox.addStretch(1)

        def listener():
            app.router.redirectTo('product_detail',
                                  image=self.image,
                                  product_id=self.id,
                                  name=self.name,
                                  cpc=self.cpc,
                                  ptype=self.ptype,
                                  description=self.description,
                                  market_hash=self.market_hash,
                                  owner_address=self.owner_address)

        image_url = wallet.market_client.url + \
            'product/v1/allproducts/images/?path=' + self.image

        image = ProductQML(None, image_url, 220, int(
            self.h), market_hash=self.market_hash)
        image.obj.signals.click.connect(listener)
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
        sales = QLabel(str(self.sales) + ' sales')
        sales.setObjectName('sales')

        hbox.addWidget(cpc)
        hbox.addWidget(cpc_unit)
        hbox.addWidget(sales)
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

        # tbox.addWidget(remain)
        tbox.addStretch(1)

        vbox.addLayout(tbox)

        tmp = QWidget()
        tmp.setLayout(vbox)
        tmp.setContentsMargins(0, 0, 0, 0)
        tmp.setObjectName('main_product')
        layout = QVBoxLayout()
        layout.addWidget(tmp)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        # self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("""
            QWidget#main_product {
                background:#ffffff;
                border:1px solid #dddddd;
                border-radius:5px;
            }
            QLabel {
                font-family:SFUIDisplay-Regular;
            }
            QLabel#image {
                border:1px solid #dddddd;
                border-radius:5px;
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
                padding: 3px 4px;
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
