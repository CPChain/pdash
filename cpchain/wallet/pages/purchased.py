import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout

from cpchain.wallet.pages import wallet, app
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
        # all products
        adapter = ProductAdapter(products)
        # all orders
        orders = app.products_order_list
        # Find my bought orders
        bought_orders = [i for i in orders if i['buyer_addr'] == app.addr]
        # Find all my bought products's hash
        products = [i['product_hash'] for i in bought_orders]
        self.products.value = adapter.filter_in('market_hash', products)

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
        pdsWidget = ProductList(self.products, show_status=True)
        layout.addWidget(pdsWidget)
        return layout
