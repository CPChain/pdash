#!/usr/bin/python3

import sys
import os
import logging

from PyQt5.QtWidgets import (QMainWindow, QApplication, QFrame, QDesktopWidget, QPushButton, QHBoxLayout, QMessageBox, QVBoxLayout, QGridLayout, QScrollArea, QListWidget, QListWidgetItem, QTabWidget, QLabel, QWidget, QLineEdit, QTableWidget, QTextEdit, QAbstractItemView, QTableWidgetItem, QMenu, QHeaderView, QAction, QFileDialog, QDialog, QRadioButton, QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, QPoint, QBasicTimer

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

# widgets
from cpchain.wallet.components.sidebar import SideBar

globalLogBeginner.beginLoggingTo([textFileLogObserver(sys.stdout)])
logger = logging.getLogger(__name__)

class Router:

    index = MarketPage
    back_stack = [('market_page', [], {})]
    forward_stack = []
    listener = []

    page = {
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
        print(Router.forward_stack)

    @staticmethod
    def forward():
        print(Router.forward_stack)
        if len(Router.forward_stack) > 0:
            page, args, kwargs = Router.forward_stack[-1]
            Router.back_stack.append((page, args, kwargs))
            Router.forward_stack = Router.forward_stack[:-1]
            Router._redirectTo(page, *args, **kwargs)

sidebarMenu = [
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
    def __init__(self, reactor):
        super().__init__()
        self.reactor = reactor
        self.body = None
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

        def add_content_tabs():
            self.content_tabs = content_tabs = QTabWidget(self)
            content_tabs.setObjectName("content_tabs")
            content_tabs.tabBar().hide()
            content_tabs.setContentsMargins(0, 0, 0, 0)

            my_data_index = content_tabs.addTab(MyDataTab(content_tabs, self), "")
            publish_product = content_tabs.addTab(PublishProduct(content_tabs), "")
            market = content_tabs.addTab(MarketPage(content_tabs), "")
            detail = content_tabs.addTab(ProductDetail(content_tabs), "")

            self.main_tab_index = {
                "my_data_tab": my_data_index,
                "publish_product_page": publish_product,
                "market_page": market,
                "product_detail": detail
            }
        # add_content_tabs()

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

    def update_purchased_tab(self, nex_tab='downloaded'):

        tab_index = self.main_tab_index['purchase_tab']
        self.content_tabs.removeTab(tab_index)
        for key in self.main_tab_index:
            if self.main_tab_index[key] > tab_index:
                self.main_tab_index[key] -= 1
        tab_index = self.content_tabs.addTab(PurchasedTab(main_wnd.content_tabs), "")
        self.main_tab_index['purchase_tab'] = tab_index
        self.content_tabs.setCurrentIndex(tab_index)
        wid = self.content_tabs.currentWidget()
        if nex_tab == 'downloading':
            wid.purchased_main_tab.setCurrentIndex(1)
        elif nex_tab == 'downloaded':
            wid.purchased_main_tab.setCurrentIndex(0)
        else:
            logger.debug("Wrong parameter!")

    def closeEvent(self, event):
        print('Close Event')
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

def initialize_system():
    def monitor_chain_event():
        monitor_new_order = LoopingCall(wallet.chain_broker.monitor.monitor_new_order)
        monitor_new_order.start(10)

        handle_new_order = LoopingCall(wallet.chain_broker.handler.handle_new_order)
        handle_new_order.start(15)

        monitor_ready_order = LoopingCall(wallet.chain_broker.monitor.monitor_ready_order)
        monitor_ready_order.start(20)

        handle_ready_order = LoopingCall(wallet.chain_broker.handler.handle_ready_order)
        handle_ready_order.start(25)

        monitor_confirmed_order = LoopingCall(wallet.chain_broker.monitor.monitor_confirmed_order)
        monitor_confirmed_order.start(30)
    monitor_chain_event()

def buildMainWnd():
    main_wnd = MainWindow(reactor)
    _handle_keyboard_interrupt()

    initialize_system()
    return main_wnd

def login():
    wallet.accounts.set_default_account(1)
    wallet.market_client.account = wallet.accounts.default_account
    wallet.market_client.public_key = ECCipher.serialize_public_key(wallet.market_client.account.public_key)
    wallet.market_client.login()

if __name__ == '__main__':
    app.router = Router
    main_wnd = buildMainWnd()
    app.main_wnd = main_wnd
    app.update()
    wallet.set_main_wnd(main_wnd)
    login()
    reactor.run()
    os._exit()
