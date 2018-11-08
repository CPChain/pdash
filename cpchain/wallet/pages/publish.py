import hashlib
import importlib
import logging
import os
import os.path as osp
import string

from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, Qt, pyqtSignal, QObject, QUrl, pyqtProperty
from PyQt5.QtGui import *
from PyQt5.QtGui import QCursor, QFont, QFontDatabase, QPixmap
from PyQt5.QtQuickWidgets import QQuickWidget
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
                                  main_wnd, wallet, qml_path)
from cpchain.wallet.simpleqt.component import Component
from cpchain.wallet.simpleqt.decorator import component, page
from cpchain.wallet.simpleqt.page import Page
from cpchain.wallet.simpleqt.basic import Builder, Input, Text
from cpchain.wallet.simpleqt.widgets import CheckBox
from cpchain.wallet.simpleqt.widgets.label import Label

logger = logging.getLogger(__name__)


class ImageUploadObject(QObject):

    def __init__(self, parent, width, height, background, text, browse_text, gap=3):
        self._width = width
        self._height = height
        self._background = background
        self._icon = abs_path('icons/add@2x.jpg')
        self._text = text
        self._browse_text = browse_text
        self._file = ""
        self._gap = gap
        return super().__init__(parent)

    @pyqtProperty(float)
    def width(self):
        return self._width

    @pyqtProperty(float)
    def height(self):
        return self._height

    @pyqtProperty(float)
    def gap(self):
        return self._gap

    @pyqtProperty(str)
    def background(self):
        return self._background

    @pyqtProperty(str)
    def icon(self):
        return self._icon

    @pyqtProperty(str)
    def text(self):
        return self._text

    @pyqtProperty(str)
    def browse_text(self):
        return self._browse_text

    @pyqtProperty(str)
    def file(self):
        return self._file

    @file.setter
    def file(self, _file):
        self._file = _file


class ImageUploadQml(Component):
    qml = qml_path('components/ImageUpload.qml')

    def __init__(self, parent=None, width=None, height=None,
                 text="Drop file here or",
                 browse_text="browse",
                 background="#fafafa",
                 gap=3):
        self.obj = ImageUploadObject(None, width, height,
                                     background, text,
                                     browse_text,
                                     gap)
        return super().__init__(parent)

    @property
    def file(self):
        return self.obj.file

    @component.ui
    def ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        widget = QQuickWidget(self)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.rootContext().setContextProperty('self', self.obj)
        widget.setSource(QUrl(self.qml))
        layout.addWidget(widget)
        return layout

class PublishProduct(QScrollArea):

    published = pyqtSignal(int)

    def __init__(self, parent=None, product_id=None, type_='Batch'):
        self.parent = parent
        self.product_id = product_id
        self.type_ = type_
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.data()
        layout = self.ui()
        widget = QWidget()
        widget.setLayout(layout)
        self.setStyleSheet(self.style())
        widget.setObjectName("publish_product_page")
        self.setWidget(widget)
        self.published.connect(self.handle_update_file)

    @page.data
    def data(self):
        return {
            'name': '',
            'description': '',
            'price': '',
            'checked': False,
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

    def ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(21)
        type_label = 'Batch' if self.type_ == 'Batch' else 'Streaming'
        # Title
        title = QLabel('Publish {} Data'.format(type_label))
        title.setObjectName('title')
        layout.addWidget(title)

        layout.addSpacing(23)
        # Name
        layout.addLayout(self.gen_row("Name:", Input.Builder(width=536, height=30).model(self.name).build()))

        # Type
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
        height = 150
        img = ImageUploadQml(width=547, height=height, gap=1)
        img.setMinimumHeight(height)
        self.cover_image = img
        layout.addLayout(self.gen_row('Cover picture:', img))

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
        layout.addSpacing(30)
        layout.addStretch(1)

        return layout

    def style(self):
        return """
            QScrollArea {
                background: #fafafa;
                padding-left: 47px;

            }
            QWidget#publish_product_page {
                background: #fafafa;
            }
            QLabel, QCheckBox, QPushButton {
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
        if name and description and tag and price and checked and self.category.value and self.cover_image.file:
            file_info = fs.get_file_by_id(self.product_id)
            self.size = file_info.size
            self.start_date = '2018-04-01 10:10:10'
            self.end_date = '2018-04-01 10:10:10'
            self.path = file_info.path
            d_publish = wallet.market_client.publish_product(self.product_id, name, _type,
                                                             description, price, tag, self.start_date,
                                                             self.end_date, self.category.value, self.cover_image.file)

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
