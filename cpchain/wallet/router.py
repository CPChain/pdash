from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from cpchain.wallet.pages.my_data import MyDataTab
from cpchain.wallet.pages.publish import PublishProduct
from cpchain.wallet.pages.market import MarketPage
from cpchain.wallet.pages.detail import ProductDetail
from cpchain.wallet.pages.purchased import PurchasedPage
from cpchain.wallet.pages.wallet_page import WalletPage
from cpchain.wallet.pages.home import Home

from cpchain.wallet.pages import app



@app.event.register(app.events.ROUTE_TO)
def route_to(event):
    Router.signal.route_to.emit(event.data)

class Signals(QObject):
    route_to = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.route_to.connect(self._route_to)

    def _route_to(self, path):
        Router.redirectTo(path)


class Router:

    index = MarketPage

    back_stack = [('market_page', [], {})]
    forward_stack = []
    listener = []
    signal = Signals()
    page_obj = dict()
    now = 'market_page'

    page = {
        'wallet': WalletPage,
        'market_page': MarketPage,
        'my_data_tab': MyDataTab,
        'publish_product': PublishProduct,
        'product_detail': ProductDetail,
        'purchased_page': PurchasedPage,
        'home': Home
    }

    @staticmethod
    def addListener(listener):
        Router.listener.append(listener)

    @staticmethod
    def removeListener(listener):
        Router.listener.remove(listener)

    @staticmethod
    def _redirectTo(page, *args, **kwargs):
        widget = Router.page_obj.get(page, None)
        if not widget or not kwargs.get('cache'):
            _page = Router.page[page](app.main_wnd.body, *args, **kwargs)
            layout_page = QVBoxLayout()
            layout_page.setContentsMargins(0, 0, 0, 0)
            layout_page.addWidget(_page)
            widget = QWidget()
            widget.setLayout(layout_page)
            Router.page_obj[page] = widget
        wid = QWidget()
        wid.setLayout(app.main_wnd.body.layout())
        Router.page_obj[Router.now] = wid
        Router.now = page
        app.main_wnd.body.setLayout(widget.layout())

    @staticmethod
    def redirectTo(page, *args, **kwargs):
        Router.forward_stack = []
        Router.back_stack.append((page, args, kwargs))
        for l in Router.listener:
            l(page)
        Router._redirectTo(page, *args, **kwargs)
        app.event.emit(app.events.ROUTER_CHANGE)


    @staticmethod
    def hasback():
        return len(Router.back_stack) > 2

    @staticmethod
    def hasprev():
        return len(Router.forward_stack) > 0

    @staticmethod
    def back():
        if len(Router.back_stack) > 2:
            Router.forward_stack.append(Router.back_stack[-1])
            Router.back_stack = Router.back_stack[:-1]
            page, args, kwargs = Router.back_stack[-1]
            Router._redirectTo(page, *args, **kwargs)
        app.event.emit(app.events.ROUTER_CHANGE)

    @staticmethod
    def forward():
        if len(Router.forward_stack) > 0:
            page, args, kwargs = Router.forward_stack[-1]
            Router.back_stack.append((page, args, kwargs))
            Router.forward_stack = Router.forward_stack[:-1]
            Router._redirectTo(page, *args, **kwargs)
        app.event.emit(app.events.ROUTER_CHANGE)
