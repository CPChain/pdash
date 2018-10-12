from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (QApplication, QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget, QRadioButton,
                             QFileDialog, QListWidget, QListWidgetItem, QComboBox)
from PyQt5.QtGui import QCursor, QFont, QFontDatabase, QPixmap
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

from cpchain import root_dir

from cpchain.wallet.utils import formatTimestamp
from cpchain.wallet.utils import eth_addr_to_string, get_address_from_public_key_object

from cpchain.wallet.pages import HorizontalLine, abs_path, get_icon, app, Binder
from cpchain.wallet.pages.other import PublishDialog

from cpchain.wallet.components.table import Table
from cpchain.wallet.components.product import Product
from cpchain.wallet.components.product_list import ProductList
from cpchain.wallet.components.upload import UploadDialog
from cpchain.wallet.components.loading import Loading
from cpchain.wallet.components.sales import Sale
from cpchain.wallet.components.purchase import PurchaseDialog
from cpchain.wallet.components.picture import Picture
from cpchain.wallet.components.order_detail import OrderDetail
from cpchain.wallet.components.gif import LoadingGif
from cpchain.wallet.components.loading import Loading

from cpchain.wallet.simpleqt import Signals
from cpchain.wallet.simpleqt.page import Page
from cpchain.wallet.simpleqt.decorator import page
from cpchain.wallet.simpleqt.widgets.label import Label
from cpchain.wallet.simpleqt.widgets import Input
from cpchain.wallet.simpleqt.model import Model
from cpchain.wallet.simpleqt.basic import Button

from datetime import datetime as dt

logger = logging.getLogger(__name__)

class DetailHeader(QWidget):

    def __init__(self, name):
        self.name = name
        super().__init__()
        self.ui()

    def ui(self):
        layout = QHBoxLayout()
        self.setObjectName('main')
        name = QLabel(self.name)
        name.setStyleSheet("""
            font-family:SFUIDisplay-Medium;
            font-size:16px;
            color:#000000;
            text-align:left;
            border-bottom: 3px solid #ddd;
        """)
        layout.addWidget(name)
        layout.addStretch(1)
        self.setLayout(layout)
        self.setStyleSheet("""
            padding-bottom: 5px;
            border: none;
            border-bottom: 1px solid #ddd;
        """)


class ProductDetail(Page):

    def __init__(self, parent=None, product_id=None, name="", image=abs_path('icons/test.png'),
                 icon=abs_path('icons/icon_batch@2x.png'),
                 category="Category", timestamp=dt.now(),
                 sales=0, cpc=0, description="", remain=0,
                 market_hash=None, owner_address=None, ptype=None):
        self.parent = parent
        self.signals = Signals()
        self.product_id = product_id
        self.name_ = name
        self.image_ = image
        self.icon = icon
        self.category = category
        self.timestamp = timestamp
        self.sales = sales
        self.cpc_ = cpc
        self.description_ = description
        self.remain = remain
        self.ptype = ptype
        self.market_hash = market_hash
        self.owner_address = owner_address
        self.is_owner = False
        self.paying = False
        super().__init__(parent)
        self.setObjectName("product_detail")

    @page.create
    def create(self):
        @app.event.register(app.events.DETAIL_UPDATE)
        def detail_update(event):
            self.signals.refresh.emit()
        @app.event.register(app.events.NEW_ORDER)
        def listenNewOrder(event):
            self.signals.refresh.emit()
        @app.event.register(app.events.CANCEL_PURCHASE)
        def cancel_purchase(event):
            self.signals.refresh.emit()
        def render(_):
            self.buying(False)
            self.refresh()
        self.signals.refresh.connect(render)
    
    def buying(self, is_buying):
        if is_buying:
            self.buy.setEnabled(False)
            self.buy_loading.show()
        else:
            self.buy.setEnabled(True)
            self.buy_loading.hide()

    @page.data
    def data(self):
        return {
            "id": self.product_id,
            "image": self.image_,
            "icon": self.icon,
            "name": self.name_,
            "category": self.category,
            "timestamp": dt.now(),
            "sales": self.sales,
            "cpc": self.cpc_,
            "remain": self.remain,
            "description": self.description_,
            "gas": 1,
            "account": 15,
            "password": "",
            "storagePath": ""
        }

    def setProduct(self, product):
        self.product = product
    
    def add_orders_ui(self, widget):
        height = widget.height()
        layout = widget.layout()

        order = None
        status = 0
        start = 1

        is_seller = self.owner_address == wallet.market_client.public_key
        # Sales
        if app.products_order.get(self.market_hash):
            self.sales_header = DetailHeader("{} Sales".format(len(app.products_order.get(self.market_hash))))
            layout.insertWidget(start, self.sales_header)
            start += 1

            # enum State {
            #     Created,
            #     SellerConfirmed,
            #     ProxyFetched,
            #     ProxyDelivered,
            #     BuyerConfirmed,
            #     Finished,
            #     SellerRated,
            #     BuyerRated,
            #     Disputed,
            #     Withdrawn
            # }
            myaddress = get_address_from_public_key_object(wallet.market_client.public_key)
            self.salesElem = []
            need_show = False
            for order in app.products_order[self.market_hash]:
                # not buyer and not seller
                buyer_addr = eth_addr_to_string(order['buyer_addr'])
                is_buyer = buyer_addr == myaddress
                if not is_buyer and not is_seller:
                    continue
                need_show = True
                self.buy.setEnabled(False)
                status = order['status']
                if status == 0:
                    current = 1
                elif status == 1:
                    current = 1
                elif status == 2:
                    current = 2
                elif status == 3:
                    current = 3
                else:
                    current = 4
                sale1 = Sale(image=abs_path('icons/avatar.jpeg'),
                             name=order['public_key'],
                             current=current,
                             timestamps=["May 2, 08:09:08", "May 2, 08:09:08", "May 2, 08:09:08", "May 2, 08:09:08"],
                             order_id=order["order_id"],
                             mhash=self.market_hash,
                             is_buyer=is_buyer,
                             is_seller=is_seller,
                             order_type='stream' if self.ptype == 'stream' else 'file')
                layout.insertWidget(start, sale1)
                self.salesElem.append(sale1)
                start += 1
                height += 200
            
            if not need_show:
                self.sales_header.hide()

        # Order Detail
        if order and self.owner_address != wallet.market_client.public_key:
            if status > 2:
                order_header = DetailHeader('Order Detail')
                layout.insertWidget(start, order_header)
                start += 1
                if self.ptype == 'file':
                    self.data_type = 'batch'
                    self.order_detail = OrderDetail(order_time=Model("2018/6/15  08:40:39"),
                                                    status=Model("Delivered on May 2, 08:09:08"),
                                                    order_id=order["order_id"],
                                                    name=self.name.value,
                                                    data_type=self.data_type)
                    layout.insertWidget(start, self.order_detail)
                    start += 1
                height += 100
                if self.ptype == 'stream':
                    self.data_type = 'stream'
                    order_detail = OrderDetail(order_time=Model("2018/6/15  08:40:39"),
                                            status=Model("Delivered on May 2, 08:09:08"),
                                            order_id=order["order_id"],
                                            market_hash=self.market_hash,
                                            name=self.name.value,
                                            data_type=self.data_type)
                    layout.insertWidget(start, order_detail)
                    start += 1
                    height += 100
        widget.setFixedHeight(height)
        

    def render_widget(self):
        height = 200
        layout = QVBoxLayout(self)
        layout.setObjectName('body')
        layout.setAlignment(Qt.AlignTop)
        header = QHBoxLayout()

        # Image
        imageWid = Picture(self.image.value, 240, 160)
        Binder.click(imageWid, lambda _: app.event.emit(app.events.DETAIL_UPDATE))
        header.addWidget(imageWid)

        right = QVBoxLayout()
        right.setAlignment(Qt.AlignTop)
        right.setSpacing(15)
        # Title
        title = Label(self.name)
        title.setObjectName('name')
        right.addWidget(title)

        # category
        catbox = QHBoxLayout()
        icon = self.icon.value
        if icon:
            iconL = QLabel()
            iconL.setMaximumWidth(20)
            iconL.setMaximumHeight(20)
            iconL.setObjectName('icon')
            iconL.setPixmap(QPixmap(icon))
            catbox.addWidget(iconL)
        category = Label(self.category)
        category.setObjectName('category')
        category.setAlignment(Qt.AlignCenter)
        category.setMaximumWidth(52)
        catbox.addWidget(category)
        catbox.addStretch(1)

        right.addLayout(catbox)

        # Timestamp and Remain Days
        tbox = QHBoxLayout()
        tmp = self.timestamp.value
        if not tmp:
            tmp = dt.now()
        tmp_str = formatTimestamp(tmp)
        timestamp = QLabel(str(tmp_str))
        timestamp.setObjectName('timestamp')
        tbox.addWidget(timestamp)
        sales = QLabel(str(self.sales.value) + ' sales')
        sales.setObjectName('sales')
        tbox.addWidget(sales)

        tbox.addStretch(1)
        right.addLayout(tbox)

        # CPC and Sales
        hbox = QHBoxLayout()
        hbox.setObjectName('hbox1')

        cpc = QLabel(str(self.cpc.value))
        cpc.setObjectName('cpc')
        cpc_unit = QLabel('CPC')
        cpc_unit.setObjectName('cpc_unit')
        hbox.addWidget(cpc)
        hbox.addWidget(cpc_unit)

        # Buy button
        def openPurchaseDialog(_):
            self.buying(True)
            if not self.paying:
                market_hash = self.market_hash
                owner_address = self.owner_address
                purchaseDlg = PurchaseDialog(self,
                                             price=self.cpc,
                                             gas=self.gas,
                                             account=self.account,
                                             storagePath=self.storagePath,
                                             password=self.password,
                                             market_hash=market_hash,
                                             name=self.name.value,
                                             owner_address=owner_address)
                purchaseDlg.show()
        self.buy = Button.Builder(width=100, height=30).text('Buy')\
                                   .style('primary')\
                                   .click(openPurchaseDialog)\
                                   .build()
        hbox.addWidget(self.buy)
        if self.owner_address == wallet.market_client.public_key:
            self.buy.setEnabled(False)

        # Buy Loading
        self.buy_loading = Loading()
        hbox.addWidget(self.buy_loading)
        self.buy_loading.hide()

        hbox.addStretch(1)

        right.addLayout(hbox)
        header.addLayout(right)
        layout.addLayout(header)

        # Description
        desc = DetailHeader('Description')
        layout.addWidget(desc)
        desc = Label(self.description)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        height += 200
        layout.addStretch(1)

        widget_ = QWidget()
        widget_.setObjectName('parent_widget')
        widget_.setLayout(layout)
        widget_.setFixedWidth(720)
        widget_.setFixedHeight(height)
        widget_.setStyleSheet(self.style())
        self.add_orders_ui(widget_)
        return widget_

    def ui(self):
        self.widget_ = self.render_widget()
        # Scroll Area Properties
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        # scroll.setFixedHeight(800)
        self.scroll.setWidget(self.widget_)
        self.setWidget(self.scroll)
        self.setWidgetResizable(True)

    def style(self):
        return """
            QWidget#parent_widget{background: transparent;}
            QVBoxLayout {
                background: #fafafa;
            }
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
        """
