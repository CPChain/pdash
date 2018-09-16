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

from cpchain.wallet.pages import load_stylesheet, wallet, main_wnd, app

globalLogBeginner.beginLoggingTo([textFileLogObserver(sys.stdout)])
logger = logging.getLogger(__name__)


# widgets

from cpchain.wallet.pages.personal import *
from cpchain.wallet.pages.product import *
from cpchain.wallet.pages.header import *
from cpchain.wallet.pages.purchase import *
from cpchain.wallet.pages.sidebar import *
from cpchain.wallet.pages.other import *

from cpchain.wallet.pages.my_data import MyDataTab
from cpchain.wallet.pages.publish import PublishProduct
from cpchain.wallet.pages.market import MarketPage
from cpchain.wallet.pages.detail import ProductDetail

class Router:

    index = MarketPage

    page = {
        'market_page': MarketPage,
        'my_data_tab': MyDataTab,
        'publish_product': PublishProduct,
        'product_detail': ProductDetail
    }

    @staticmethod
    def redirectTo(page, *args, **kwargs):
        _page = Router.page[page](app.main_wnd.body, *args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(_page)
        QWidget().setLayout(app.main_wnd.body.layout())
        app.main_wnd.body.setLayout(layout)

sidebarMenu = [
    {
        'name': 'Market',
        'icon': 'market@2x.png',
        'link': 'market_page'
    }, {
        'name': 'My Data',
        'icon': 'my data@2x.png',
        'link': 'my_data_tab'
    }
]

class MainWindow(QMainWindow):
    def __init__(self, reactor):
        super().__init__()
        self.reactor = reactor
        self.body = None
        self.init_ui()


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
            
            self.pop_index = content_tabs.addTab(PopularTab(content_tabs), "")
            self.cloud_index = content_tabs.addTab(CloudTab(content_tabs), "")
            self.follow_index = content_tabs.addTab(FollowingTab(content_tabs), "")
            self.sell_index = content_tabs.addTab(SellTab(content_tabs), "")
            content_tabs.addTab(PersonalProfileTab(content_tabs), "")
            content_tabs.addTab(TagHPTab(content_tabs), "")
            content_tabs.addTab(SellerHPTab(content_tabs), "")
            content_tabs.addTab(SecurityTab(content_tabs), "")
            content_tabs.addTab(PreferenceTab(content_tabs), "")
            content_tabs.addTab(PersonalInfoPage(content_tabs), "")
            self.purchase_index = content_tabs.addTab(PurchasedTab(content_tabs), "")
            self.collect_index = content_tabs.addTab(CollectedTab(content_tabs), "")

            my_data_index = content_tabs.addTab(MyDataTab(content_tabs, self), "")
            publish_product = content_tabs.addTab(PublishProduct(content_tabs), "")
            market = content_tabs.addTab(MarketPage(content_tabs), "")
            detail = content_tabs.addTab(ProductDetail(content_tabs), "")

            self.main_tab_index = {
                "popular_tab": self.pop_index,
                "follow_tab": self.follow_index,
                "cloud_tab": self.cloud_index,
                "selling_tab": self.sell_index,
                "purchase_tab": self.purchase_index,
                "collect_tab": self.collect_index,
                "my_data_tab": my_data_index,
                "publish_product_page": publish_product,
                "market_page": market,
                "product_detail": detail
            }
        add_content_tabs()

        header = Header(self)
        sidebar = SideBar(self, self, sidebarMenu)

        def set_layout():
            main_layout = QVBoxLayout()
            main_layout.setSpacing(0)
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

    # initialize_system()
    return main_wnd


if __name__ == '__main__':
    main_wnd = buildMainWnd()
    app.main_wnd = main_wnd
    app.router = Router
    wallet.set_main_wnd(main_wnd)
    try:
        reactor.run()
        os._exit()
    except Exception as e:
        print(e)
