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

from cpchain.wallet.pages import main_wnd
from cpchain.wallet.pages.other import PublishDialog

from datetime import datetime as dt

class ProductList(QFrame):

    def __init__(self, products, col=3):
        self.col = col
        self.products = products
        super().__init__()
        self.initUI()

    def setProducts(self, products):
        self.products = products
        self.initUI()

    def initUI(self):
        pds = self.products
        layout = QGridLayout()
        row = int((len(pds) + self.col / 2) / self.col + 0.5)
        for i in range(row):
            for j in range(self.col):
                index = i * self.col + j
                if index < len(pds):
                    layout.addWidget(pds[index], i, j)
                else:
                    layout.addWidget(QLabel(''), i, j)
        self.setLayout(layout)
        self.setObjectName('main')
        self.setStyleSheet("""
            #main {
                
            }
        """)
