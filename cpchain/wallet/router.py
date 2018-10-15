from PyQt5.QtWidgets import QVBoxLayout, QWidget

from cpchain.wallet.pages.my_data import MyDataTab
from cpchain.wallet.pages.publish import PublishProduct
from cpchain.wallet.pages.market import MarketPage
from cpchain.wallet.pages.detail import ProductDetail
from cpchain.wallet.pages.purchased import PurchasedPage
from cpchain.wallet.pages.wallet_page import WalletPage

from cpchain.wallet.pages import app

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
