import hashlib
import importlib
import logging
import os
import os.path as osp
import string

from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtGui import QCursor, QFont, QFontDatabase, QPixmap
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QCheckBox, QComboBox,
                             QDialog, QFileDialog, QFrame, QGridLayout,
                             QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QMenu, QMessageBox,
                             QPushButton, QRadioButton, QScrollArea,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QTextEdit, QVBoxLayout, QWidget)
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread

from cpchain import root_dir
from cpchain.crypto import ECCipher, Encoder, RSACipher
from cpchain.proxy.client import pick_proxy
from cpchain.utils import open_file, sizeof_fmt
from cpchain.wallet import fs
from cpchain.wallet.components.loading import Loading
from cpchain.wallet.components.product import Product
from cpchain.wallet.components.product_list import ProductList
from cpchain.wallet.components.table import Table
from cpchain.wallet.components.upload import UploadDialog
from cpchain.wallet.pages import (Binder, HorizontalLine, abs_path, app,
                                  get_icon, get_pixm, load_stylesheet,
                                  main_wnd, wallet)
from cpchain.wallet.simpleqt.component import Component
from cpchain.wallet.simpleqt.decorator import component, page
from cpchain.wallet.simpleqt.page import Page
from cpchain.wallet.simpleqt.basic import Builder, Input, Text
from cpchain.wallet.simpleqt.widgets import CheckBox
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
        palette1.setBrush(self.backgroundRole(), QtGui.QBrush(
            QtGui.QPixmap(abs_path('icons/close'))))
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
        add = Picture(path=abs_path('icons/add@2x.jpg'),
                      width=width, height=height)
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

    published = pyqtSignal(int)

    def __init__(self, parent=None, product_id=None, type_='Batch'):
        self.parent = parent
        self.product_id = product_id
        self.type_ = type_
        super().__init__(parent)
        self.setObjectName("publish_product_page")
        self.published.connect(self.handle_update_file)

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

    def gen_row(self, left_text, *widgets, **kw):
        row = QHBoxLayout()
        row.setSpacing(0)
        left_widget = Builder().text(left_text).name('left').build()
        width = kw.get('left_width', 110)
        left_widget.setMinimumWidth(width)
        left_widget.setMaximumWidth(width)
        row.addWidget(left_widget)
        row.addSpacing(10)
        for widget in widgets:
            if isinstance(widget, QWidget):
                row.addWidget(widget)
            elif isinstance(widget, int):
                row.addSpacing(widget)
        row.addStretch(1)
        return row

    @page.ui
    def ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(21)

        # Title
        title = QLabel('Publish Batch Data')
        title.setObjectName('title')
        layout.addWidget(title)

        layout.addSpacing(23)
        # Name
        layout.addLayout(self.gen_row("Name:", Input.Builder(width=536, height=30).model(self.name).build()))

        # Type
        type_label = 'Batch' if self.type_ == 'Batch' else 'Streaming'
        layout.addLayout(self.gen_row('Type:', QLabel('{} data'.format(type_label))))

        # Category
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
        layout.addLayout(self.gen_row("Category:", categoryWid))

        # Cover Picture
        openBtn = QLabel('browse...')
        openBtn.setObjectName('openBtn')

        def onOpen(_):
            tmp = QFileDialog.getOpenFileName()[0]
            if tmp:
                self.cover_image.value = tmp
        Binder.click(openBtn, onOpen)
        path = Label(self.cover_image)
        layout.addLayout(self.gen_row('Cover picture:', openBtn))
        layout.addLayout(self.gen_row("", path))

        # Description
        text = Text.Builder(width=536, height=80).model(self.description).build()
        # text.setMaximumHeight(80)
        # text.setMinimumHeight(80)
        # text.setMaximumWidth(536)
        # text.setMinimumWidth(536)
        layout.addLayout(self.gen_row("Description:", text))

        # Price
        layout.addLayout(self.gen_row("Price:", Input.Builder(width=160, height=30).model(self.price).build(), 14, QLabel('CPC')))

        # Agreement
        agreement = QLabel("xxxxxx")
        agreement.setObjectName('agreement')
        layout.addLayout(self.gen_row("", CheckBox(self.checked), 9, QLabel("I agree with the agreement of"), 5, agreement))

        # Bottom
        cancel = QPushButton('Cancel')
        cancel.setObjectName('pinfo_cancel_btn')
        cancel.clicked.connect(self.handle_cancel)
        ok = QPushButton('Publish')
        ok.setObjectName('pinfo_publish_btn')
        ok.clicked.connect(self.handle_publish)
        layout.addLayout(self.gen_row("", cancel, 20, ok))
        layout.addStretch(1)
        return layout

    @page.style
    def style(self):
        return """
            QScrollArea#publish_product_page {
                padding-left: 47px;

            }
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

    def handle_update_file(self, status):
        if status == 1:
            def cb(products):
                pass
            wallet.market_client.products().addCallbacks(cb)
            QMessageBox.information(
                self, "Tips", "Update market side product successfully !")
            self.handle_cancel()
        else:
            QMessageBox.information(
                self, "Tips", "Update market side product Failed!")

    def handle_publish(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
            return
        name = self.name.value
        _type = 'file' if self.type_ == 'Batch' else 'stream'
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
                d = wallet.market_client.update_file_info(
                    self.product_id, market_hash)

                def handle_update_file(status):
                    self.published.emit(status)
                d.addCallback(handle_update_file)
            d_publish.addCallback(update_table)
        else:
            QMessageBox.warning(
                self, "Warning", "Please fill out the necessary selling information first!")

    def handle_cancel(self):
        app.router.back()
