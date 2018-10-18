import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout

from cpchain.wallet.pages import wallet
from cpchain.wallet.pages import abs_path
from cpchain.wallet import fs
from cpchain.wallet.components.product_list import ProductList
from cpchain.wallet.simpleqt.page import Page
from cpchain.wallet.simpleqt.decorator import page

from cpchain.wallet.adapters import ProductAdapter

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
        self.products.value = ProductAdapter(products).data

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
