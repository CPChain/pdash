from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget, QRadioButton,
                             QFileDialog, QListWidget, QListWidgetItem, QComboBox)
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
import hashlib

from cpchain import root_dir

from cpchain.wallet.pages import HorizontalLine, abs_path, get_icon, app
from cpchain.wallet.pages.other import PublishDialog

from cpchain.wallet.components.table import Table
from cpchain.wallet.components.product import Product
from cpchain.wallet.components.product_list import ProductList
from cpchain.wallet.components.upload import UploadDialog
from cpchain.wallet.components.loading import Loading

logger = logging.getLogger(__name__)

class Pictures(QFrame):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)
        self.setStyleSheet("""
            QFrame {
                background: white;
            }
        """)

class PublishProduct(QScrollArea):

    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.parent = parent
        self.product_id = product_id
        self.setObjectName("publish_product_page")

        self.init_ui()

    def init_ui(self):
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
        self.pinfo_title_edit = QLineEdit()
        layout.addWidget(self.pinfo_title_edit, 3, 2, 1, COL - 1)

        # Type
        layout.addWidget(QLabel('Type:'), 4, 1, 1, 1)
        layout.addWidget(QLabel('Batch data'), 4, 2, 1, 2)

        # Category
        layout.addWidget(QLabel('Category:'), 5, 1, 1, 1)
        category = [
            'Transportation',
            'Test1',
            'Test2'
        ]
        categoryWid = QComboBox()
        for cate in category:
            categoryWid.addItem(cate)
        layout.addWidget(categoryWid, 5, 2, 1, 1)

        # Cover Picture
        layout.addWidget(QLabel('Cover picture:'), 6, 1, 1, 1)
        layout.addWidget(Pictures(), 6, 2, 5, COL - 1)

        # Description
        layout.addWidget(QLabel('Description:'), 12, 1, 1, 1)
        description = QTextEdit()
        description.setMaximumHeight(100)
        self.pinfo_descrip_edit = description
        layout.addWidget(description, 12, 2, 2, COL - 1)

        # Price
        layout.addWidget(QLabel('Price:'), 14, 1, 1, 1)
        priceHbox = QHBoxLayout()
        priceHbox.setContentsMargins(0, 0, 0, 0)
        self.pinfo_price_edit = QLineEdit()
        priceHbox.addWidget(self.pinfo_price_edit)
        priceHbox.addWidget(QLabel('CPC'))
        priceHbox.addStretch(1)
        priceWidget = QWidget()
        priceWidget.setLayout(priceHbox)
        layout.addWidget(priceWidget, 14, 2, 1, 2)

        # Agreement
        aggHBox = QHBoxLayout()
        aggHBox.setContentsMargins(0, 0, 0, 0)
        aggHBox.setAlignment(Qt.AlignLeft)
        self.pinfo_checkbox = QCheckBox()
        aggHBox.addWidget(self.pinfo_checkbox)
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
        self.setLayout(layout)
        self.setStyleSheet("""
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
        """)

    def setProduct(self, product_id):
        self.product_id = product_id

    def handle_publish(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
            return
        self.pinfo_title = self.pinfo_title_edit.text()
        self.pinfo_type = 'file'
        self.pinfo_descrip = self.pinfo_descrip_edit.toPlainText()
        self.pinfo_tag = 'tag1'
        self.pinfo_price = self.pinfo_price_edit.text()
        self.pinfo_checkbox_state = self.pinfo_checkbox.isChecked()
        if self.pinfo_title and self.pinfo_descrip and self.pinfo_tag and self.pinfo_price and self.pinfo_checkbox_state:

            file_info = fs.get_file_by_id(self.product_id)
            self.size = file_info.size
            self.start_date = '2018-04-01 10:10:10'
            self.end_date = '2018-04-01 10:10:10'
            self.path = file_info.path
            self.file_md5 = hashlib.md5(open(self.path, "rb").read()).hexdigest()
            logger.debug(self.file_md5)
            d_publish = wallet.market_client.publish_product(self.product_id, self.pinfo_title, self.pinfo_type,
                                                             self.pinfo_descrip, self.pinfo_price,
                                                             self.pinfo_tag, self.start_date,
                                                             self.end_date)
            def update_table(market_hash):
                d = wallet.market_client.update_file_info(self.product_id, market_hash)
                def handle_update_file(status):
                    if status == 1:
                        QMessageBox.information(self, "Tips", "Update market side product successfully !")
                        self.handle_cancel()
                d.addCallback(handle_update_file)
            d_publish.addCallback(update_table)
        else:
            QMessageBox.warning(self, "Warning", "Please fill out the necessary selling information first!")

    def handle_cancel(self):
        wid = app.main_wnd.content_tabs.findChild(QWidget, 'my_data_tab')
        app.main_wnd.content_tabs.setCurrentWidget(wid)
