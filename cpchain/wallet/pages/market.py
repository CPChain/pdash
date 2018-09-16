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

from cpchain.wallet.pages import HorizontalLine, abs_path, get_icon, Binder
from cpchain.wallet.pages.other import PublishDialog

from cpchain.wallet.components.table import Table
from cpchain.wallet.components.product import Product
from cpchain.wallet.components.product_list import ProductList
from cpchain.wallet.components.upload import UploadDialog
from cpchain.wallet.components.loading import Loading

logger = logging.getLogger(__name__)

class MarketPage(QScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("market_page")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        banner = QLabel(self)
        path = abs_path('icons/banner 2.png')
        pixmap = QPixmap(path)
        pixmap = pixmap.scaled(720, 155)
        banner.setPixmap(pixmap)
        layout.addWidget(banner)

        # Product List
        test_dict = dict(image=abs_path('icons/test.png'),
                         icon=abs_path('icons/icon_batch@2x.png'),
                         name="Name of a some published data name of a data")
        products = []
        for i in range(15):
            product = Product(**test_dict)
            products.append(product)

        pdsWidget = ProductList(products)
        layout.addWidget(pdsWidget)

        widget = QWidget()
        widget.setObjectName('parent_widget')
        widget.setLayout(layout)
        widget.setFixedWidth(750)
        widget.setStyleSheet("QWidget#parent_widget{background: white;}")

        # Scroll Area Properties
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(False)
        scroll.setWidget(widget)

        vLayout = QVBoxLayout(self)
        vLayout.addWidget(scroll)
        self.setLayout(vLayout)
