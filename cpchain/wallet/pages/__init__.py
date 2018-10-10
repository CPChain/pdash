import os.path as osp
import string
import copy
from cpchain import config, root_dir

from PyQt5.QtWidgets import QFrame, QMessageBox
from PyQt5.QtGui import QIcon, QCursor, QPixmap, QFont, QFontDatabase

from twisted.internet import reactor
from cpchain.wallet.wallet import Wallet
from cpchain.wallet import events
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

class HorizontalLine(QFrame):
    def __init__(self, parent=None, wid=2, color="#ccc"):
        super().__init__(parent)
        self.parent = parent
        self.wid = wid
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(self.wid)
        self.setStyleSheet("QFrame{{ border-top: {}px solid {};}}".format(wid, color))

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

class App:

    def __init__(self):
        self.main_wnd = None
        self.username = None
        self.products_order = {}
        self.event = event
        self.events = events
        self.status_ = {}
        self.init()
    
    def init(self):
        @event.register(events.SELLER_DELIVERY)
        def seller_delivery(event):
            self.update(events.DETAIL_UPDATE, event.data)
        @event.register(events.BUYER_RECEIVE)
        def buyer_receive(event):
            self.update(events.DETAIL_UPDATE, event.data)
        @event.register(events.BUYER_CONFIRM)
        def buyer_receive(event):
            self.update(events.DETAIL_UPDATE, event.data)
        
        @event.register(events.PAY)
        def pay(event):
            self.update()
            self.event.emit(events.NEW_ORDER, event.data)

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
        def callback(orders):
            # Trigger Events
            old_orders = copy.deepcopy(self.products_order)
            self.products_order = copy.deepcopy(orders)
            if pre_event:
                self.event.emit(pre_event, data)
            if not self.products_order:
                return
        d = wallet.chain_broker.query_seller_products_order(None)
        d.addCallbacks(callback)

app = App()
