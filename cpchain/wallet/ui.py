#!/usr/bin/python3

import sys
import os
import logging
import shelve

from PyQt5.QtWidgets import (QMainWindow, QApplication, QFrame, QDesktopWidget, QPushButton, QHBoxLayout, QMessageBox, QVBoxLayout, QGridLayout, QScrollArea, QListWidget, QListWidgetItem, QTabWidget, QLabel, QWidget, QLineEdit, QTableWidget, QTextEdit, QAbstractItemView, QTableWidgetItem, QMenu, QHeaderView, QAction, QFileDialog, QDialog, QRadioButton, QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, QPoint, QBasicTimer
from PyQt5 import QtCore, QtWidgets


from cpchain.proxy.client import pick_proxy

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.logger import globalLogBeginner, textFileLogObserver


from cpchain.crypto import ECCipher

from cpchain.wallet.pages import load_stylesheet, wallet, main_wnd, app
from cpchain.wallet.pages.header import Header
from cpchain.wallet.pages.my_data import MyDataTab
from cpchain.wallet.pages.publish import PublishProduct
from cpchain.wallet.pages.market import MarketPage
from cpchain.wallet.pages.detail import ProductDetail
from cpchain.wallet.pages.purchased import PurchasedPage

from cpchain.wallet.pages.login import LoginWindow
from cpchain.wallet.pages.wallet_page import WalletPage


# widgets
from cpchain.wallet.components.sidebar import SideBar

from cpchain.wallet import events
from cpchain.wallet.simpleqt import event
from cpchain.account import Account, get_balance
from cpchain.wallet import utils
from cpchain.chain.utils import default_w3 as web3

globalLogBeginner.beginLoggingTo([textFileLogObserver(sys.stdout)])
logger = logging.getLogger(__name__)

class Router:

    index = WalletPage
    back_stack = [('market_page', [], {})]
    forward_stack = []
    listener = []

    page = {
        'wallet': WalletPage,
        'market_page': MarketPage,
        'my_data_tab': MyDataTab,
        'publish_product': PublishProduct,
        'product_detail': ProductDetail,
        'purchased_page': PurchasedPage
    }

    @staticmethod
    def addListener(listener):
        Router.listener.append(listener)

    @staticmethod
    def removeListener(listener):
        Router.listener.remove(listener)

    @staticmethod
    def _redirectTo(page, *args, **kwargs):
        _page = Router.page[page](app.main_wnd.body, *args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(_page)
        QWidget().setLayout(app.main_wnd.body.layout())
        app.main_wnd.body.setLayout(layout)

    @staticmethod
    def redirectTo(page, *args, **kwargs):
        Router.forward_stack = []
        Router.back_stack.append((page, args, kwargs))
        for l in Router.listener:
            l(page)
        Router._redirectTo(page, *args, **kwargs)

    @staticmethod
    def hasBack():
        return len(Router.back_stack) > 1

    @staticmethod
    def back():
        if len(Router.back_stack) > 1:
            Router.forward_stack.append(Router.back_stack[-1])
            Router.back_stack = Router.back_stack[:-1]
            page, args, kwargs = Router.back_stack[-1]
            Router._redirectTo(page, *args, **kwargs)

    @staticmethod
    def forward():
        if len(Router.forward_stack) > 0:
            page, args, kwargs = Router.forward_stack[-1]
            Router.back_stack.append((page, args, kwargs))
            Router.forward_stack = Router.forward_stack[:-1]
            Router._redirectTo(page, *args, **kwargs)

sidebarMenu = [
    {
        'name': 'Wallet',
        'icon': 'wallet@2x.png',
        'link': 'wallet'
    },
    {
        'name': 'Market',
        'icon': 'market@2x.png',
        'link': 'market_page'
    }, {
        'name': 'My Data',
        'icon': 'my data@2x.png',
        'link': 'my_data_tab'
    }, {
        'name': 'Purchased Data',
        'icon': 'purchased data@2x.png',
        'link': 'purchased_page'
    }
]

class MainWindow(QMainWindow):
    
    def search_handler(self, val):
        app.router.redirectTo('market_page', search=val)

    search_signal = QtCore.pyqtSignal(str, name="modelChanged")

    def __init__(self, reactor):
        super().__init__()
        self.reactor = reactor
        self.body = None
        self.search_signal.connect(self.search_handler)
        self.init_ui()
        self.content_tabs = None


    def init_ui(self):
        self.setWindowTitle('CPChain Wallet')
        self.setObjectName("main_window")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.main_tab_index = {}

        def set_geometry():
            self.resize(1002, 710)  # resize before centering.
            self.setMinimumSize(800, 500)
            center_pt = QDesktopWidget().availableGeometry().center()
            qrect = self.frameGeometry()
            qrect.moveCenter(center_pt)
            self.move(qrect.topLeft())
        set_geometry()

        header = Header(self)
        sidebar = SideBar(sidebarMenu)

        def set_layout():
            main_layout = QVBoxLayout()
            main_layout.setAlignment(Qt.AlignHCenter)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addWidget(header)

            content_layout = QHBoxLayout()
            content_layout.setSpacing(0)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.addWidget(sidebar)
            self.body = QWidget()
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(Router.index(self.body))
            self.body.setLayout(layout)
            content_layout.addWidget(self.body)
            main_layout.addLayout(content_layout)
            wid = QWidget(self)
            wid.setLayout(main_layout)
            self.setCentralWidget(wid)
        set_layout()
        load_stylesheet(self, "main_window.qss")

        self.show()


    def closeEvent(self, event):
        self.reactor.stop()
        os._exit(0)

def _handle_keyboard_interrupt():
    def sigint_handler(*args):
        QApplication.quit()

    import signal
    signal.signal(signal.SIGINT, sigint_handler)

    from PyQt5.QtCore import QTimer

    _handle_keyboard_interrupt.timer = QTimer()
    timer = _handle_keyboard_interrupt.timer
    timer.start(300)
    timer.timeout.connect(lambda: None)

def __unlock():
    try:
        web3.personal.unlockAccount(app.addr, app.pwd)
    except Exception as e:
        logger.error(e)

def initialize_system():
    def monitor_chain_event():
        monitor_new_order = LoopingCall(wallet.chain_broker.monitor.monitor_new_order)
        monitor_new_order.start(10)

        handle_new_order = LoopingCall(wallet.chain_broker.handler.handle_new_order)
        handle_new_order.start(10)

        monitor_ready_order = LoopingCall(wallet.chain_broker.monitor.monitor_ready_order)
        monitor_ready_order.start(20)

        handle_ready_order = LoopingCall(wallet.chain_broker.handler.handle_ready_order)
        handle_ready_order.start(25)

        monitor_confirmed_order = LoopingCall(wallet.chain_broker.monitor.monitor_confirmed_order)
        monitor_confirmed_order.start(30)
    if hasattr(wallet, 'chain_broker'):
        monitor_chain_event()
        update = LoopingCall(app.update)
        update.start(10)
        app.update()

def buildMainWnd():
    main_wnd = MainWindow(reactor)
    _handle_keyboard_interrupt()
    return main_wnd

def __login(account=None):
    if account is None:
        wallet.accounts.set_default_account(1)
        account = wallet.accounts.default_account
    public_key = ECCipher.serialize_public_key(account.public_key)
    addr = utils.get_address_from_public_key_object(public_key)
    addr = web3.toChecksumAddress(addr)
    logger.info(addr)
    logger.info(get_balance(addr))
    app.addr = addr
    app.pwd = account.key_passphrase.decode()
    wallet.market_client.account = account
    wallet.market_client.public_key = ECCipher.serialize_public_key(wallet.market_client.account.public_key)
    wallet.market_client.login(app.username).addCallbacks(lambda _: event.emit(events.LOGIN_COMPLETED))
    wallet.init()
    initialize_system()

def enterPDash(account=None):
    if app.main_wnd:
        __login(account)
        return
    app.router = Router
    main_wnd = buildMainWnd()
    QtWidgets.qApp.setApplicationDisplayName('PDash')

    app.main_wnd = main_wnd

    wallet.set_main_wnd(main_wnd)
    __login(account)


def login():
    path = os.path.expanduser('~/.cpchain')
    if not os.path.exists(path):
        os.mkdir(path)
    with shelve.open(os.path.join(path, 'account')) as file:
        key_path = file.get('key_path')
        key_passphrase = file.get('key_passphrase')
        try:
            if key_path and key_passphrase:
                account = Account(key_path, key_passphrase)
                public_key = ECCipher.serialize_public_key(account.public_key)
                addr = utils.get_address_from_public_key_object(public_key)
                addr = web3.toChecksumAddress(addr)
                logger.info(addr)
                logger.info(get_balance(addr))
                app.addr = addr
                app.pwd = key_passphrase.decode()
                __unlock()
                enterPDash(account)
                return
        except Exception as e:
            logger.error(e)
    logger.debug('Init')
    wnd = LoginWindow(reactor)
    wnd.show()
    wallet.set_main_wnd(wnd)

def save_login_info():
    path = os.path.expanduser('~/.cpchain')
    if not os.path.exists(path):
        os.mkdir(path)
    with shelve.open(os.path.join(path, 'account')) as file:
        file['key_path'] = wallet.market_client.account.key_path
        file['key_passphrase'] = wallet.market_client.account.key_passphrase


def search(event):
    search = event.data
    wallet.main_wnd.search_signal.emit(search)
    

def init_handlers():
    event.register(events.LOGIN_COMPLETED, lambda _: save_login_info())
    event.register(events.SEARCH, search)


if __name__ == '__main__':
    app.unlock = __unlock
    wallet.app = app
    app.enterPDash = enterPDash
    init_handlers()
    login()
    app.unlock()
    reactor.run()
