from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget, QRadioButton,
                             QFileDialog, QListWidget, QListWidgetItem, QComboBox)
from PyQt5.QtGui import QCursor, QFont, QFontDatabase, QPixmap

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

from cpchain import root_dir

from cpchain.wallet.pages import HorizontalLine, abs_path, get_icon
from cpchain.wallet.pages.other import PublishDialog

from cpchain.wallet.components.table import Table
from cpchain.wallet.components.product import Product
from cpchain.wallet.components.product_list import ProductList
from cpchain.wallet.components.upload import UploadDialog
from cpchain.wallet.components.loading import Loading

from datetime import datetime as dt

logger = logging.getLogger(__name__)

class ProductDetail(QScrollArea):

    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.parent = parent
        self.product_id = product_id
        self.setObjectName("product_detail")

        self.product = {
            "id": 1,
            "image": abs_path('icons/test.png'),
            "icon": abs_path('icons/icon_batch@2x.png'),
            "name": "Name of a some published data name of a data",
            "category": "category",
            "timestamp": dt.now(),
            "sales": 128,
            "cpc": 25,
            "remain": 0,
            "description": ("The MarketPsych Indices is a cryptocurrency sentiment data feed."
                            "  Over 43 sentiments and themes are extracted from the text of the top 2,000 "
                            "global news and 800 financial social media sites covering 130+ cryptocurrencies.  "
                            "News and social media feeds are aggregated independently.  The data is delivered "
                            "in minutely, hourly, and daily feeds.")
        }

        self.init_ui()

    def setProduct(self, product):
        self.product = product

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        header = QHBoxLayout()

        # Image
        image = QPixmap(self.product['image'])
        image = image.scaled(240, 160)
        imageWid = QLabel()
        imageWid.setPixmap(image)
        header.addWidget(imageWid)

        right = QVBoxLayout()
        right.setAlignment(Qt.AlignTop)
        right.setSpacing(15)
        # Title
        title = QLabel(self.product['name'])
        title.setObjectName('name')
        right.addWidget(title)

        # category
        catbox = QHBoxLayout()
        icon = self.product['icon']
        if icon:
            iconL = QLabel()
            iconL.setMaximumWidth(20)
            iconL.setMaximumHeight(20)
            iconL.setObjectName('icon')
            iconL.setPixmap(QPixmap(icon))
            catbox.addWidget(iconL)
        category = QLabel(self.product['category'])
        category.setObjectName('category')
        category.setAlignment(Qt.AlignCenter)
        category.setMaximumWidth(52)
        catbox.addWidget(category)
        catbox.addStretch(1)

        right.addLayout(catbox)

        # Timestamp and Remain Days
        tbox = QHBoxLayout()
        tmp = self.product['timestamp']
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
        sales = QLabel(str(self.product['sales']) + ' sales')
        sales.setObjectName('sales')
        tbox.addWidget(sales)

        tbox.addStretch(1)
        right.addLayout(tbox)

        # CPC and Sales
        hbox = QHBoxLayout()
        hbox.setObjectName('hbox1')

        cpc = QLabel(str(self.product['cpc']))
        cpc.setObjectName('cpc')
        cpc_unit = QLabel('CPC')
        cpc_unit.setObjectName('cpc_unit')
        hbox.addWidget(cpc)
        hbox.addWidget(cpc_unit)
        hbox.addStretch(1)

        right.addLayout(hbox)

        header.addLayout(right)

        layout.addLayout(header)

        tab = QLabel('Description')
        tab.setObjectName('desc_tap')
        layout.addWidget(tab)
        desc = QLabel(self.product['description'])
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.setLayout(layout)

        self.setStyleSheet("""
            QLabel {
                font-family:SFUIDisplay-Regular;
            }
            #desc_tap {
                margin-top: 20px;
                font-size:16px;
                padding-bottom: 5px;
            }
            #name {
                font-family:SFUIDisplay-Semibold;
                font-size:20px;
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
