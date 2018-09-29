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

from cpchain.wallet.pages import HorizontalLine, abs_path, get_icon, Binder, app
from cpchain.wallet.pages.other import PublishDialog

from cpchain.wallet.components.table import Table
from cpchain.wallet.components.banner import Banner
from cpchain.wallet.components.product import Product
from cpchain.wallet.components.product_list import ProductList
from cpchain.wallet.components.upload import UploadDialog
from cpchain.wallet.components.loading import Loading

from cpchain.wallet.simpleqt.page import Page
from cpchain.wallet.simpleqt.decorator import page
from cpchain.wallet.simpleqt.widgets.label import Label

logger = logging.getLogger(__name__)

class MarketPage(Page):

    def __init__(self, parent=None, search=None):
        self.parent = parent
        self.search = search
        super().__init__(parent)
        self.setObjectName("market_page")

    @page.create
    def create(self):
        wallet.market_client.products(self.search).addCallbacks(self.renderProducts)

    @page.method
    def renderProducts(self, products):
        _products = []
        for i in products:
            test_dict = dict(image=i['cover_image'] or abs_path('icons/test.png'),
                             icon=abs_path('icons/icon_batch@2x.png'),
                             name=i['title'],
                             cpc=i['price'],
                             description=i['description'],
                             market_hash=i["msg_hash"],
                             owner_address=i['owner_address'])
            _products.append(test_dict)
        self.products.value = _products

    @page.data
    def data(self):
        return {
            'products': []
        }

    @page.ui
    def ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        path = abs_path('icons/banner 2.png')
        banner = Banner(path,
                        width=720,
                        height=155,
                        title="PDASH",
                        subtitle="Parallel Distributed Architecture for Data Storage and Sharing")
        layout.addWidget(banner)

        # Product List
        pdsWidget = ProductList(self.products)
        layout.addWidget(pdsWidget)
        return layout
