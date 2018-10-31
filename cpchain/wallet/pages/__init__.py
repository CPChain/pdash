from enum import Enum
import os.path as osp
import string
import copy
import time
import logging
from cpchain import config, root_dir

from PyQt5.QtWidgets import QFrame, QMessageBox
from PyQt5.QtGui import QIcon, QCursor, QPixmap, QFont, QFontDatabase

from twisted.internet import reactor
from cpchain.wallet import events
from cpchain.wallet.wallet import Wallet
from cpchain.wallet.simpleqt import event

wallet = Wallet(reactor)

global main_wnd

main_wnd = None


def abs_path(path):
    return osp.join(root_dir, "cpchain/assets/wallet", path)


def load_stylesheet(wid, name):
    path = osp.join(root_dir, "cpchain/assets/wallet/qss", name)
    subs = dict(asset_dir=osp.join(root_dir, "cpchain/assets/wallet"))
    with open(path) as f:
        s = string.Template(f.read())
        wid.setStyleSheet(s.substitute(subs))


def qml_path(path):
    return osp.join(root_dir, "cpchain/assets/wallet/qml", path)


class HorizontalLine(QFrame):
    def __init__(self, parent=None, wid=2, color="#ccc"):
        super().__init__(parent)
        self.parent = parent
        self.wid = wid
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(self.wid)
        self.setStyleSheet(
            "QFrame{{ border-top: {}px solid {};}}".format(wid, color))


def get_icon(name):
    path = osp.join(root_dir, "cpchain/assets/wallet/icons", name)
    return QIcon(path)


def get_pixm(name):
    path = osp.join(root_dir, "cpchain/assets/wallet/icons", name)
    return QPixmap(path)


class Binder:

    @staticmethod
    def click(obj, listener):
        setattr(obj, 'mousePressEvent', listener)


def warning(parent, msg="Please input all the required fields first"):
    QMessageBox.warning(parent, "Warning", msg)


class OrderStatus(Enum):

    created = 1

    delivering = 2

    delivered = 3

    receiving = 4

    received = 5

    confirming = 6

    confirmed = 7


class App:

    def __init__(self):
        self.start_at = time.time()
        self.last_at = 0
        self.main_wnd = None
        self.username = None
        self.products_order = {}
        self.event = event
        self.events = events
        self.addr = None
        self.login_open = False
        self.status_ = {}
        self.init()
    
    def timing(self, logger, hint):
        self.last_at = time.time()
        logger.debug('[%s] %.4fs'%(hint, (self.last_at - self.start_at)))

    def init(self):
        @event.register(events.SELLER_DELIVERY)
        def seller_delivery(event):
            self.update(events.DETAIL_UPDATE, event.data)

        @event.register(events.BUYER_RECEIVE)
        def buyer_receive(event):
            self.update(events.DETAIL_UPDATE, event.data)

        @event.register(events.BUYER_CONFIRM)
        def buyer_confirm(event):
            self.update(events.DETAIL_UPDATE, event.data)

        @event.register(events.PAY)
        def pay(event):
            self.update()
            self.event.emit(events.NEW_ORDER, event.data)

        @event.register(events.LOGIN_OPEN)
        def set_login_true(_):
            self.login_open = True

        @event.register(events.LOGIN_CLOSE)
        def set_login_false(_):
            self.login_open = False

    def find(self, new_, order_id):
        for item in new_:
            if order_id == item['order_id']:
                return item
        return None

    def list2dict(self, orders):
        result = dict()
        for item in orders:
            result[item['order_id']] = item
        return result

    def update(self, pre_event=None, data=None):
        if self.login_open:
            return
        def callback(orders):
            # Trigger Events
            self.products_order = copy.deepcopy(orders)
            if pre_event:
                self.event.emit(pre_event, data)
            if not self.products_order:
                return
        d = wallet.chain_broker.query_seller_products_order(None)
        d.addCallbacks(callback)

    def get_status_enum(self, status):
        status_enum = None
        if status == 0:
            status_enum = OrderStatus.created
        if status == 1:
            status_enum = OrderStatus.delivered
        elif status == 2:
            status_enum = OrderStatus.receiving
        elif status == 3:
            status_enum = OrderStatus.received
        elif status >= 4:
            status_enum = OrderStatus.confirmed
        return status_enum

    def get_status(self, market_hash, buyer_addr):
        for order in self.products_order.get(market_hash, []):
            if order['buyer_addr'] == buyer_addr:
                return order['status']
        return None

    @property
    def products_order_list(self):
        orders = []
        for product, order_list in self.products_order.items():
            for i in order_list:
                i['product_hash'] = product
                status = i['status']
                i['status_enum'] = self.get_status_enum(status)
            orders += order_list
        return orders


app = App()
