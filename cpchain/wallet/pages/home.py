from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtWidgets import QVBoxLayout

from cpchain import account
from cpchain.wallet.pages import abs_path, app, qml_path, wallet
from cpchain.wallet.components.product_list import ProductList
from cpchain.wallet.simpleqt.decorator import page
from cpchain.wallet.simpleqt.page import Page

from cpchain.wallet.adapters import ProductAdapter



class HomeObject(QObject):
    iconChanged = pyqtSignal()
    usernameChanged = pyqtSignal()
    amountChanged = pyqtSignal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._icon = abs_path('icons/person.png')
        self._username = ""
        self._amount = "0"

    @pyqtProperty(str, notify=iconChanged)
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        if self._icon == value:
            return
        self._icon = value
        self.iconChanged.emit()

    @pyqtProperty(str, notify=usernameChanged)
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        if self._username == value:
            return
        self._username = value
        self.usernameChanged.emit()

    @pyqtProperty(str, notify=amountChanged)
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        if self._amount == value:
            return
        self._amount = value
        self.amountChanged.emit()

    @pyqtSlot()
    def to_wallet(self):
        app.event.emit(app.events.ROUTE_TO, 'wallet')


class Home(Page):

    qml = qml_path('home.qml')

    def __init__(self, parent):
        self.obj = HomeObject()
        super().__init__(parent)

    @page.method
    def renderProducts(self, products):
        self.products.value = ProductAdapter(products).data

    @page.data
    def data(self):
        return {
            'products': []
        }

    @page.create
    def create(self):
        # balance
        amount = account.get_balance(app.addr)
        self.obj.icon = abs_path('icons/person.png')
        self.obj.username = 'Hi, {}'.format(app.username)
        self.obj.amount = '{}'.format(amount)
        wallet.market_client.products().addCallbacks(self.renderProducts)

    @page.ui
    def ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        widget = QQuickWidget(self)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.rootContext().setContextProperty('self', self.obj)
        widget.setSource(QtCore.QUrl(self.qml))
        layout.addWidget(widget)
        pdsWidget = ProductList(self.products)
        layout.addWidget(pdsWidget)
        return layout
