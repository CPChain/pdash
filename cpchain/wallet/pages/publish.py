from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget, QRadioButton,
                             QFileDialog, QListWidget, QListWidgetItem, QComboBox)
from PyQt5.QtGui import QCursor, QFont, QFontDatabase, QPixmap
from PyQt5.QtGui import *
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
import hashlib

from cpchain import root_dir

from cpchain.wallet.pages import HorizontalLine, abs_path, get_icon, app, Binder
from cpchain.wallet.pages.other import PublishDialog

from cpchain.wallet.components.table import Table
from cpchain.wallet.components.product import Product
from cpchain.wallet.components.product_list import ProductList
from cpchain.wallet.components.upload import UploadDialog
from cpchain.wallet.components.loading import Loading

from cpchain.wallet.simpleqt.component import Component
from cpchain.wallet.simpleqt.page import Page
from cpchain.wallet.simpleqt.decorator import page, component
from cpchain.wallet.simpleqt.widgets import Input, TextEdit, CheckBox
from cpchain.wallet.simpleqt.widgets.label import Label

logger = logging.getLogger(__name__)

class Picture(QWidget):

    def __init__(self, path, width, height):
        self.width = width
        self.height = height
        self.path = path
        super().__init__()
        self.ui()
        self.style()

    @component.method
    def brush(self):
        palette1 = QtGui.QPalette()
        palette1.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap(abs_path('icons/close'))))
        self.setPalette(palette1)
        self.setAutoFillBackground(True)

    @component.ui
    def ui(self):
        if self.layout():
            QWidget().setLayout(self.layout())
        # self.setMinimumWidth(self.width)
        # self.setMaximumWidth(self.width)
        # self.setMinimumHeight(self.height)
        # self.setMaximumHeight(self.height)
        pic = QLabel()
        pic.setPixmap(QPixmap(self.path))
        pic.setMinimumWidth(self.width)
        pic.setMaximumWidth(self.width)
        pic.setMinimumHeight(self.height)
        pic.setMaximumHeight(self.height)

        mylayout = QVBoxLayout()
        mylayout.addWidget(pic)
        mylayout.setAlignment(Qt.AlignHCenter)
        return mylayout

    @component.style
    def style(self):
        return """

        """

class Pictures(QFrame):

    def __init__(self):
        super().__init__()
        self.data()
        self.ui()
        self.style()

    @component.data
    def data(self):
        return {
            'pictures': [abs_path('icons/add@2x.jpg')]
        }

    def read_file(self, _):
        file_choice = QFileDialog.getOpenFileName()[0]

    @component.ui
    def ui(self):
        width = 150
        height = 150
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignLeft)
        for pic in self.pictures.value:
            tmp = Picture(path=pic, width=width, height=height)
            layout.addWidget(tmp)
        add = Picture(path=abs_path('icons/add@2x.jpg'), width=width, height=height)
        Binder.click(add, self.read_file)
        layout.addWidget(add)
        return layout

    @component.style
    def style(self):
        return """
            QFrame {
                background: white;
            }
        """

class PublishProduct(Page):

    def __init__(self, parent=None, product_id=None, type_='batch'):
        self.parent = parent
        self.product_id = product_id
        self.type_ = type_
        super().__init__(parent)
        self.setObjectName("publish_product_page")

    @page.data
    def data(self):
        return {
            'name': '',
            'description': '',
            'price': '',
            'checked': False,
            'cover_image': '',
            'category': 'Advertising'
        }

    @page.ui
    def ui(self):
        layout = QGridLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(20)
        COL = 8
        # Title
        title = QLabel('Publish Batch Data')
        title.setObjectName('title')
        layout.addWidget(title, 1, 1, 2, COL)

        # Name
        layout.addWidget(QLabel('Name:'), 3, 1, 1, 1)
        layout.addWidget(Input(self.name), 3, 2, 1, COL - 1)

        # Type
        layout.addWidget(QLabel('Type:'), 4, 1, 1, 1)
        type_label = 'Batch' if self.type_ == 'batch' else 'Streaming'
        layout.addWidget(QLabel('{} data'.format(type_label)), 4, 2, 1, 2)

        # Category
        layout.addWidget(QLabel('Category:'), 5, 1, 1, 1)
        category = [
            'Advertising',
            'Business Intelligence',
            'Communications',
            'Crypto',
            'Energy',
            'Entertainment',
            'Environment',
            'Finance',
            'Health',
            'Industrial',
            'IoT',
            'Other',
            'Retail',
            'Smart Cities',
            'Social Media',
            'Sports',
            'Transportation',
            'Weather'
        ]
        categoryWid = QComboBox()
        for cate in category:
            categoryWid.addItem(cate)
        def itemSelect(index):
            self.category.value = category[index]
        categoryWid.currentIndexChanged.connect(itemSelect)
        layout.addWidget(categoryWid, 5, 2, 1, 1)

        # Cover Picture
        layout.addWidget(QLabel('Cover picture:'), 6, 1, 1, 1)
        openBtn = QLabel('open...')
        openBtn.setObjectName('openBtn')
        def onOpen(_):
            tmp = QFileDialog.getOpenFileName()[0]
            if tmp:
                self.cover_image.value = tmp
        Binder.click(openBtn, onOpen)
        path = Label(self.cover_image)
        layout.addWidget(openBtn, 6, 2)
        layout.addWidget(path, 8, 2)

        # Description
        layout.addWidget(QLabel('Description:'), 12, 1, 1, 1)
        description = QTextEdit()
        description.setMaximumHeight(100)
        layout.addWidget(TextEdit(self.description), 12, 2, 2, COL - 1)

        # Price
        layout.addWidget(QLabel('Price:'), 14, 1, 1, 1)
        priceHbox = QHBoxLayout()
        priceHbox.setContentsMargins(0, 0, 0, 0)
        priceHbox.addWidget(Input(self.price))
        priceHbox.addWidget(QLabel('CPC'))
        priceHbox.addStretch(1)
        priceWidget = QWidget()
        priceWidget.setLayout(priceHbox)
        layout.addWidget(priceWidget, 14, 2, 1, 2)

        # Agreement
        aggHBox = QHBoxLayout()
        aggHBox.setContentsMargins(0, 0, 0, 0)
        aggHBox.setAlignment(Qt.AlignLeft)
        aggHBox.addWidget(CheckBox(self.checked))
        aggHBox.addWidget(QLabel("I agree with the agreement of"))
        agreement = QLabel("xxxxxx")
        agreement.setObjectName('agreement')
        aggHBox.addWidget(agreement)
        aggHBox.addStretch(1)
        aggWidget = QWidget()
        aggWidget.setLayout(aggHBox)
        layout.addWidget(aggWidget, 15, 2)

        # Bottom
        btm = QHBoxLayout()
        btm.setContentsMargins(0, 0, 0, 0)
        btm.setSpacing(20)
        aggHBox.setAlignment(Qt.AlignLeft)
        cancel = QPushButton('Cancel')
        cancel.setObjectName('pinfo_cancel_btn')
        cancel.clicked.connect(self.handle_cancel)
        btm.addWidget(cancel)
        ok = QPushButton('Publish')
        ok.setObjectName('pinfo_publish_btn')
        ok.clicked.connect(self.handle_publish)
        btm.addWidget(ok)
        btm.addStretch(1)

        btmWidget = QWidget()
        btmWidget.setContentsMargins(0, 0, 0, 0)
        btmWidget.setObjectName("btm")
        btmWidget.setLayout(btm)
        btmWidget.setStyleSheet("#btm {padding: 0px 0px 0px 0px;}")
        layout.addWidget(btmWidget, 16, 2)
        return layout
    
    @page.style
    def style(self):
        return """
            QLabel, QCheckBox, QPushButton {
                font-family:SFUIDisplay-Regular;
            }

            #title {
                font-size:24px;
            }

            #agreement {
                color: #3984f7;
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

            QLabel#openBtn {
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

            QPushButton#pinfo_publish_btn{
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

            QPushButton#pinfo_publish_btn:hover{
                background: #3984f7; 
                border: 1px solid #3984f7;
            }

            QPushButton#pinfo_publish_btn:pressed{
                border: 1px solid #2e6dcd; 
                background: #2e6dcd;
            }

            QPushbutton#pinfo_publish_btn:disabled{
                border: 1px solid #8cb8ea; 
                background: #98b9eb;
            }
        """

    def setProduct(self, product_id):
        self.product_id = product_id

    def handle_publish(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
            return
        name = self.name.value
        _type = 'file' if self.type_ == 'batch' else 'stream'
        description = self.description.value
        tag = 'tag1'
        price = self.price.value
        checked = self.checked.value
        if name and description and tag and price and checked and self.category.value and self.cover_image.value:
            file_info = fs.get_file_by_id(self.product_id)
            self.size = file_info.size
            self.start_date = '2018-04-01 10:10:10'
            self.end_date = '2018-04-01 10:10:10'
            self.path = file_info.path
            d_publish = wallet.market_client.publish_product(self.product_id, name, _type,
                                                             description, price, tag, self.start_date,
                                                             self.end_date, self.category.value, self.cover_image.value)
            def update_table(market_hash):
                d = wallet.market_client.update_file_info(self.product_id, market_hash)
                def handle_update_file(status):
                    if status == 1:
                        def cb(products):
                            pass
                        wallet.market_client.products().addCallbacks(cb)
                        QMessageBox.information(self, "Tips", "Update market side product successfully !")
                        self.handle_cancel()
                    else:
                        QMessageBox.information(self, "Tips", "Update market side product Failed!")
                d.addCallback(handle_update_file)
            d_publish.addCallback(update_table)
        else:
            QMessageBox.warning(self, "Warning", "Please fill out the necessary selling information first!")

    def handle_cancel(self):
        app.router.back()
