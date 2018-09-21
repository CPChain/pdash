import os.path as osp
import string
from cpchain import config, root_dir

from PyQt5.QtWidgets import QFrame, QMessageBox
from PyQt5.QtGui import QIcon, QCursor, QPixmap, QFont, QFontDatabase

from twisted.internet import reactor
from cpchain.wallet.wallet import Wallet

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
        self.setStyleSheet("QFrame{{ border-top: 1px solid {};}}".format(color))

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
        self.products_order = {}

    def update(self):
        def callback(orders):
            print(orders)
            self.products_order = orders
        d = wallet.chain_broker.query_seller_products_order(None)
        d.addCallbacks(callback)

app = App()
