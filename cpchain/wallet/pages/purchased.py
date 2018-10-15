import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout

from cpchain.wallet.pages import wallet
from cpchain.wallet.pages import abs_path
from cpchain.wallet import fs
from cpchain.wallet.components.product_list import ProductList
from cpchain.wallet.simpleqt.page import Page
from cpchain.wallet.simpleqt.decorator import page

logger = logging.getLogger(__name__)

class PurchasedPage(Page):
    
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(parent)

    @page.create
    def create(self):
        wallet.market_client.products().addCallbacks(self.renderProducts)

    @page.method
    def renderProducts(self, products):
        records = fs.get_buyer_file_list()
        _products = []
        for i in products:
            test_dict = dict(image=abs_path('icons/test.png'),
                             icon=abs_path('icons/icon_batch@2x.png'),
                             name=i['title'],
                             cpc=i['price'],
                             description=i['description'])
            _products.append(test_dict)
        self.products.value = _products

    @page.data
    def data(self):
        return {
            'products': []
        }

    @page.ui
    def ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        # Product List
        pdsWidget = ProductList(self.products)
        layout.addWidget(pdsWidget)
        return layout
