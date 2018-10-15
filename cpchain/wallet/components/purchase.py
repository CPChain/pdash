import logging
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QComboBox,
                             QVBoxLayout, QWidget, QDialog, QFileDialog)

from cpchain.wallet.pages import wallet, app
from cpchain.proxy.client import pick_proxy

from cpchain.wallet.simpleqt.decorator import page
from cpchain.wallet.simpleqt.widgets.label import Label
from cpchain.wallet.simpleqt.widgets import Input, ComboBox
from cpchain.wallet.simpleqt.model import ListModel

logger = logging.getLogger(__name__)

class PurchaseDialog(QDialog):

    def __init__(self, parent, title="Purchase Confirmation", width=524, height=405,
                 price=None, gas=None, account=None, password=None, storagePath=None,
                 market_hash=None, name=None, owner_address=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(width, height)
        self.price = price
        self.gas = gas
        self.account = account
        self.password = password
        self.storagePath = storagePath
        self.market_hash = market_hash
        self.name = name
        self.proxy = ListModel([])
        self.owner_address = owner_address
        self.ui()
        self.style()
        self.init_proxy()

    @page.method
    def init_proxy(self):
        def set_proxy(proxy):
            self.proxy.value = proxy
        pick_proxy().addCallbacks(set_proxy)
    

    def gen_row(self, name, widget, width=None):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        nameWid = QLabel(name)
        nameWid.setMinimumWidth(150)
        nameWid.setObjectName("name")
        layout.addWidget(nameWid)
        layout.addWidget(widget)
        if width:
            widget.setMinimumWidth(width)
        if isinstance(widget, Label):
            unit = Label('CPC')
            unit.setObjectName('unit')
            widget.setObjectName('value')
            layout.addWidget(unit)
        tmp = QWidget()
        tmp.setLayout(layout)
        tmp.setObjectName('item')
        return tmp

    @page.ui
    def ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(self.gen_row('Price: ', Label(self.price)))
        layout.addWidget(self.gen_row('Gas: ', Label(self.gas)))
        layout.addWidget(self.gen_row('Account Ballance: ', Label(self.account)))
        pwd = Input(self.password)
        pwd.setEchoMode(Input.Password)
        layout.addWidget(self.gen_row('Payment Password: ', pwd))
        layout.addWidget(self.gen_row('Proxy: ', ComboBox(self.proxy), 160))


        # Bottom
        btm = QHBoxLayout()
        btm.setAlignment(Qt.AlignRight)
        btm.setContentsMargins(0, 0, 0, 0)
        btm.setSpacing(40)
        btm.addStretch(1)
        cancel = QPushButton('Cancel')
        cancel.setObjectName('pinfo_cancel_btn')
        cancel.clicked.connect(self.handle_cancel)
        btm.addWidget(cancel)
        ok = QPushButton('Pay')
        ok.setObjectName('pinfo_publish_btn')
        ok.clicked.connect(self.handle_confirm)
        btm.addWidget(ok)
        layout.addSpacing(30)
        layout.addLayout(btm)
        return layout

    def handle_confirm(self):
        def get_proxy_address(proxy_addr):
            msg_hash = self.market_hash
            file_title = self.name
            proxy = proxy_addr
            seller = self.owner_address
            app.unlock()
            wallet.chain_broker.handler.buy_product(msg_hash, file_title, proxy, seller)
        get_proxy_address(self.proxy.current)
        app.event.emit(app.events.CLICK_PAY)
        self.close()

    def handle_cancel(self):
        app.event.emit(app.events.CANCEL_PURCHASE)
        self.close()

    @page.style
    def style(self):
        return """
            QLabel#browse {
                font-family:SFUIDisplay-Medium;
                font-size:14px;
                color:#0073df;
                text-align:right;
                margin-left: 440px;
            }
            QLabel#name {
                font-family:SFUIDisplay-Regular;
                font-size:14px;
                color:#000000;
            }
            Label#value {
                font-family:SFUIDisplay-Regular;
                font-size:18px;
                color:#000000;
            }
            QWidget#item {
                margin-top: 20px;
                margin-bottom: 20px;
            }
            QPushButton#pinfo_cancel_btn{
                padding-left: 10px;
                padding-right: 10px;
                border: 1px solid #3173d8; 
                border-radius: 3px;
                color: #3173d8;
                min-height: 30px;
                max-height: 30px;
                background: #ffffff;
                min-width: 80px;
                max-width: 80px;
            }

            QPushButton#pinfo_cancel_btn:hover{
                border: 1px solid #3984f7; 
                color: #3984f6;
            }

            QPushButton#pinfo_cancel_btn:pressed{
                border: 1px solid #2e6dcd; 
                color: #2e6dcd;
                background: #e5ecf4;
            }

            QPushbutton#pinfo_cancel_btn:disabled{
                border: 1px solid #8cb8ea; 
                color: #8cb8ea;
            }

            QPushButton#pinfo_publish_btn{
                padding-left: 10px;
                padding-right: 10px;
                border: 1px solid #3173d8; 
                border-radius: 3px;
                color: #ffffff;
                min-height: 30px;
                max-height: 30px;
                min-width: 80px;
                max-width: 80px;
                background: #3173d8;
            }

            QPushButton#pinfo_publish_btn:hover{
                background: #3984f7; 
                border: 1px solid #3984f7;
            }

            QPushButton#pinfo_publish_btn:pressed{
                border: 1px solid #2e6dcd; 
                background: #2e6dcd;
            }

            QPushbutton#pinfo_publish_btn:disabled{
                border: 1px solid #8cb8ea; 
                background: #98b9eb;
            }
        """