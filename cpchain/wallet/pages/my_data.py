from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget, QRadioButton,
                             QFileDialog, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QCursor, QFont, QFontDatabase

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

from cpchain.wallet.pages import main_wnd, HorizontalLine, abs_path, get_icon, Binder, app
from cpchain.wallet.pages.other import PublishDialog

from cpchain.wallet.components.table import Table
from cpchain.wallet.components.product import Product
from cpchain.wallet.components.product_list import ProductList
from cpchain.wallet.components.upload import UploadDialog
from cpchain.wallet.components.stream_upload import StreamUploadDialog
from cpchain.wallet.components.loading import Loading
from cpchain.wallet.pages.publish import PublishProduct

from cpchain.wallet.simpleqt import Page
from cpchain.wallet.simpleqt.decorator import page
from cpchain.wallet.simpleqt.widgets.label import Label
from cpchain.wallet.simpleqt.basic import Builder, Button, Line

logger = logging.getLogger(__name__)

class MyDataTab(Page):

    def __init__(self, parent=None, main_wnd=None):
        self.parent = parent
        self.main_wnd = main_wnd
        super().__init__(parent)
        self.setObjectName("my_data_tab")

    @page.create
    def create(self):
        # My Products
        wallet.market_client.myproducts().addCallbacks(self.renderProducts)

    @page.method
    def renderProducts(self, products):
        _products = []
        for i in products:
            test_dict = dict(image=i['cover_image'] or abs_path('icons/test.png'),
                             icon=abs_path('icons/icon_batch@2x.png'),
                             name=i['title'],
                             cpc=i['price'],
                             description=i['description'])
            _products.append(test_dict)
        self.products.value = _products

    @page.data
    def data(self):
        return {
            'products': [],
            'table_data': [],
            'stream_data': [

            ]
        }

    @page.ui
    def ui(self, vLayout):
        def buildTable():
            header = {
                'headers': ['Name', 'Location', 'Size', 'Status'],
                'width': [282, 170, 170, 54]
            }
            data = fs.get_file_list()
            self.table_data.value = data
            def buildProductClickListener(product_id):
                def listener(event):
                    app.router.redirectTo('publish_product', product_id=product_id)
                return listener
            def itemHandler(data):
                items = []
                items.append(data.name)
                items.append(data.remote_type)
                items.append(sizeof_fmt(data.size))
                status = data.is_published
                wid = QLabel('Published')
                if not status:
                    wid.setText('Publish as product')
                    wid.setStyleSheet("QLabel{color: #006bcf;}")
                    Binder.click(wid, buildProductClickListener(data.id))
                items.append(wid)
                return items

            table = Table(self, header, self.table_data, itemHandler, sort=None)
            table.setObjectName('my_table')
            table.setFixedWidth(800)
            if len(self.table_data.value) > 0:
                table.setMinimumHeight(180)
            else:
                table.setMaximumHeight(40)
            return table
        table = buildTable()
        self.table = table
        self.buildTable = buildTable

        def buildStreamTable():
            header = {
                'headers': ['Name', 'Location', 'Status'],
                'width': [327, 295, 54]
            }
            data = fs.get_file_list()
            self.stream_data.value = data
            def buildProductClickListener(product_id):
                def listener(event):
                    app.router.redirectTo('publish_product', product_id=product_id, type_='stream')
                return listener
            def itemHandler(data):
                items = []
                items.append(data.name)
                items.append(data.remote_type)
                status = data.is_published
                wid = QLabel('Published')
                if not status:
                    wid.setText('Publish as product')
                    wid.setStyleSheet("QLabel{color: #006bcf;}")
                    Binder.click(wid, buildProductClickListener(data.id))
                items.append(wid)
                return items

            table = Table(self, header, self.stream_data, itemHandler, sort=None)
            table.setObjectName('my_table')
            table.setFixedWidth(800)
            if len(self.table_data.value) > 0:
                table.setMinimumHeight(180)
            else:
                table.setMaximumHeight(40)
            return table
        stream_table = buildStreamTable()
        self.stream_table = stream_table
        self.buildStreamTable = buildStreamTable
        
        self.addH(Button.Builder(width=150, height=30)
                        .style('primary').name('btn')
                        .text('Upload Batch Data')
                        .click(self.onClickUpload).build(), 6)
        self.addH(Button.Builder(width=180, height=30)
                        .name('btn')
                        .text('Upload Streaming Data')
                        .click(self.onClickStreamUpload).build())
        self.add(space=10)

        # Line
        self.add(Line(wid=1, color="#dadada"))

        # My Product
        self.add(Builder().text('My Product').name('label_hint').build())

        # Product List
        pdsWidget = ProductList(self.products, scroll=False)
        width = 800
        pdsWidget.setMinimumWidth(width)
        pdsWidget.setMaximumWidth(width)
        self.add(pdsWidget)

        # Batch Data
        self.add(Builder().text('Batch Data').name('label_hint').build())
        self.add(table)

        if len(self.table_data.value) == 0:
            # No Data
            self.add(Builder().text('0 Batch Data!').name('no_data').build())
        
        # Stream Data
        self.add(Builder().text('Streaming Data').name('label_hint').build())
        self.add(stream_table)

        if len(self.stream_data.value) == 0:
            # No Data
            self.add(Builder().text('0 Streaming Data!').name('no_data').build())
        

        return vLayout
    
    def style(self):
        margin_left = '20'
        return """
        QPushButton#btn {
            margin-top: 20px;
            margin-left: 20px;
        }
        QLabel#no_data {
            text-align: center;
            color: #aaa;
            margin-left: 310px;
        }

        QLabel#label_hint {
            font-family:SFUIDisplay-Regular;
            font-size: 24px;
            font-weight: 700;
            margin-top: 20px;
            margin-bottom: 10px;
            margin-left: 20px;
        }

        QTableWidgetItem#publishText {
            color: blue;
        }
        """

    def onClickUpload(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
            return
        def oklistener():
            app.router.redirectTo('my_data_tab')
            # self.main_layout.removeWidget(self.table)
            # self.table.deleteLater()
            # self.table = self.buildTable()
            # self.main_layout.addWidget(self.table)
            self.upload.close()
        self.upload = UploadDialog(self, oklistener)
        self.upload.show()
    
    def onClickStreamUpload(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
            return
        def oklistener():
            app.router.redirectTo('my_data_tab')
            # self.main_layout.removeWidget(self.table)
            # self.table.deleteLater()
            # self.table = self.buildTable()
            # self.main_layout.addWidget(self.table)
            self.upload.close()
        self.upload = StreamUploadDialog(self, oklistener)
        self.upload.show()
