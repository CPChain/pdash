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
from cpchain.wallet.components.loading import Loading
from cpchain.wallet.pages.publish import PublishProduct

from cpchain.wallet.simpleqt.page import Page
from cpchain.wallet.simpleqt.decorator import page
from cpchain.wallet.simpleqt.widgets.label import Label

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
        wallet.market_client.products().addCallbacks(self.renderProducts)

    @page.method
    def renderProducts(self, products):
        _products = []
        for i in products:
            test_dict = dict(image=abs_path('icons/test.png'),
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
            'table_data': []
        }

    @page.ui
    def ui(self):
        btn_group = [
            {
                'id': 'upload_btn',
                'name': 'Upload Batch Data',
                'listener': self.onClickUpload
            }
        ]
        def buildBtnLayout(btn_group):
            btn_layout = QHBoxLayout(self)
            btn_layout.setAlignment(Qt.AlignLeft)
            for item in btn_group:
                btn = QPushButton(item['name'])
                btn.setObjectName(item['id'])
                btn.setMaximumWidth(200)
                btn.clicked.connect(item['listener'])
                btn_layout.addWidget(btn)
                btn_layout.addSpacing(5)
            return btn_layout

        def buildTable():
            header = {
                'headers': ['Name', 'Location', 'Size', 'Status'],
                'width': [252, 140, 140, 138]
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

            table = Table(self, header, self.table_data, itemHandler, sort=2)
            table.setObjectName('my_table')
            table.setFixedWidth(700)
            table.setMinimumHeight(180)
            return table
        table = buildTable()
        self.table = table
        self.buildTable = buildTable
        

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)

        # Button Group
        main_layout.addLayout(buildBtnLayout(btn_group))
        main_layout.addSpacing(2)

        # Line
        main_layout.addWidget(HorizontalLine(self, 2))

        # My Product
        my_product_label = QLabel('My Product')
        my_product_label.setObjectName('label_hint')
        main_layout.addWidget(my_product_label)

        # Product List
        pdsWidget = ProductList(self.products)
        pdsWidget.setMinimumHeight(250)
        main_layout.addWidget(pdsWidget)

        # Batch Data
        batch_label = QLabel('Batch Data')
        batch_label.setObjectName('label_hint')
        main_layout.addWidget(batch_label)

        main_layout.addWidget(table)
        main_layout.addStretch(1)
        self.main_layout = main_layout

        widget = QWidget()
        widget.setObjectName('parent_widget')
        widget.setLayout(main_layout)
        widget.setFixedWidth(750)
        widget.setStyleSheet("""
            QWidget#parent_widget{background: white;}
            QPushButton#upload_btn{
                padding-left: 16px;
                padding-right: 16px;
                border: 1px solid #3173d8; 
                border-radius: 3px;
                color: #ffffff;
                min-height: 30px;
                max-height: 30px;
                background: #3173d8;
                margin-left: 20px;
                /*background:linear-gradient(-120deg, #119bf0 1%, #167ce9 100%);*/
                /*box-shadow:0 2px 7px 0 rgba(0,0,0,0.10);*/
            }

            QPushButton#upload_btn:hover{
                background: #3984f7; 
                border: 1px solid #3984f7;
            }

            QPushButton#upload_btn:pressed{
                border: 1px solid #2e6dcd; 
                background: #2e6dcd;
            }

            QPushbutton#upload_btn:disabled{
                border: 1px solid #8cb8ea; 
                background: #98b9eb;
            }
            
        """)

        # Scroll Area Properties
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        vLayout = QVBoxLayout(self)
        vLayout.addWidget(scroll)
        load_stylesheet(self, "my_data.qss")
        return vLayout

    def onClickUpload(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
            return
        def oklistener():
            self.main_layout.removeWidget(self.table)
            self.table.deleteLater()
            self.table = self.buildTable()
            self.main_layout.addWidget(self.table)
        upload = UploadDialog(self, oklistener)
        upload.show()
