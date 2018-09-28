
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout

from cpchain.wallet.pages import wallet
from cpchain.wallet.pages import abs_path
from cpchain.wallet.simpleqt import Page
from cpchain.wallet.simpleqt.decorator import page

from cpchain.wallet.simpleqt.basic import Builder, Button

logger = logging.getLogger(__name__)

class WalletPage(Page):

    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(parent)

    @page.create
    def create(self):
        pass

    @page.data
    def data(self):
        return {
            'balance': 1000.00
        }

    def ui(self, layout):
        layout.setAlignment(Qt.AlignTop)
        self.add(Builder().text('Balance').name('title').build())
        self.addH(Builder().text(self.balance.value).name('amount').build())
        self.addH(Builder().text('CPC').name('unit').build())
        return layout

