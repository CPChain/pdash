
import logging
import time
import webbrowser
from datetime import datetime as dt

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMessageBox,
                             QVBoxLayout)
from twisted.internet.threads import deferToThread

from cpchain import account
from cpchain.chain.utils import default_w3 as web3
from cpchain.utils import config
from cpchain.wallet.components.dialog import Dialog
from cpchain.wallet.components.loading import Loading
from cpchain.wallet.components.table import Table
from cpchain.wallet.pages import app, wallet
from cpchain.wallet.simpleqt import Page
from cpchain.wallet.simpleqt.basic import Builder, Button, Input, Label, Line
from cpchain.wallet.simpleqt.decorator import component, page

logger = logging.getLogger(__name__)

UPDATE = app.event.Event()


class Record:
    category = ""
    payer = ""
    amount = 0
    time = ""

    def __init__(self, **kw):
        for k, v in kw.items():
            self.__dict__[k] = v


class ReceiveDialog(Dialog):

    def __init__(self, parent=None, oklistener=None, address=None):
        width = 540
        height = 230
        title = "Receive Token"
        self.oklistener = oklistener
        self.address = address
        self.data()
        super().__init__(wallet.main_wnd, title=title, width=width, height=height)

    @component.data
    def data(self):
        return {
            "address": self.address
        }

    def close(self):
        app.event.emit(UPDATE)
        super().close()

    def show_copyed(self):
        self.copyed.show()

        def hide():
            time.sleep(2)
            self.copyed.hide()
        deferToThread(hide)

    def copy_address(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.address.value)
        self.show_copyed()

    def openUrl(self, url):
        try:
            webbrowser.get('chrome').open_new_tab(url)
        except:
            webbrowser.open_new_tab(url)

    def ui(self, widget):
        layout = QVBoxLayout(widget)
        row = QHBoxLayout()
        row.addWidget(Builder().text('Address:').name('address_hint').build())
        row.addWidget(Builder().text(
            self.address.value).name('address').build())
        row.addStretch(1)
        layout.addLayout(row)
        row2 = QHBoxLayout()
        row2.setAlignment(Qt.AlignBottom)
        row2.addWidget(Button.Builder(width=50, height=25).click(
            self.copy_address).text('copy').name('copy').build())
        self.copyed = Builder().text('copyed!').name('copyed').build()
        row2.addWidget(self.copyed)
        self.copyed.hide()
        row2.addStretch(1)
        layout.addLayout(row2)
        layout.addWidget(Builder().text('Get CPC for free').name('get_cpc').click(
            lambda _: self.openUrl(config.account.charge_server)).build())
        return layout

    def style(self):
        return super().style() + """
        QLabel {
            font-family:SFUIDisplay-Medium;
            font-size:15px;
        }
        QLabel#address_hint {
            margin-top: 10px;
            font-weight: 700;
            margin-left: 15px;
        }
        QLabel#address {
            margin-top: 10px;
            font-weight: 500;
        }
        QLabel#get_cpc {
            margin-top: 10px;
            color:#0073df;
            font-size: 12px;
            margin-left: 15px;
        }
        QPushButton#copy {
            margin-top: 10px;
            margin-left: 15px;
        }
        QLabel#copyed {
            color: #0073df;
            font-size: 12px;
            margin-top: 8px;
        }
        """


class SendDialog(Dialog):

    def __init__(self, parent=None, oklistener=None, gas=10, account_amount=None, address=None):
        width = 480
        height = 380
        title = "Send Token"
        self.gas = gas
        self.account_amount = account_amount
        self.address = address
        self.oklistener = oklistener
        self.data()
        super().__init__(wallet.main_wnd, title=title, width=width, height=height)

    @component.data
    def data(self):
        return {
            "account_amount": self.account_amount,
            "transfer_amount": 0,
            "remark": "",
            "gas": self.gas,
            "payaddr": self.address,
            "collection_address": "",
        }

    def openPassword(self, _):
        pwd = PasswordDialog(value=self.transfer_amount.value,
                             payer_account=self.payaddr.value,
                             payee_account=self.collection_address.value)
        self.close()
        pwd.show()

    def ui(self, widget):
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        unit1 = Builder().text('CPC').name('unit').build()
        unit2 = Builder().text('CPC').name('unit').build()
        unit3 = Builder().text('CPC').name('unit').build()
        layout.addLayout(self.gen_row('Balance:', Builder().text(
            self.account_amount.value).build(), unit1))
        layout.addLayout(self.gen_row('Transfer Amount:', Input.Builder(
            height=25, width=120).model(self.transfer_amount).build(), unit2))
        layout.addLayout(self.gen_row('Remark:', Input.Builder(
            height=25, width=120).model(self.remark).build()))
        layout.addLayout(self.gen_row('Collection Address:', Input.Builder(
            height=25, width=250).model(self.collection_address).build()))
        layout.addLayout(self.gen_row('Payment Address:', Input.Builder(
            height=25, width=250).model(self.payaddr).build()))
        layout.addLayout(self.gen_row(
            'Gas Price:', Builder().text(self.gas.value).build(), unit3))

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        next_ = Button.Builder(width=100, height=28).style(
            'primary').click(self.openPassword).text('Next').build()
        hbox.addWidget(next_)
        hbox.addSpacing(5)

        layout.addLayout(hbox)
        return layout

    def style(self):
        return super().style() + """
        QLabel#left {
            text-align: right;
        }
        """


class PasswordDialog(Dialog):

    error = QtCore.pyqtSignal(str, name='error')

    def __init__(self, parent=None, oklistener=None, value=None, payer_account=None, payee_account=None):
        width = 420
        height = 210
        title = "Password"
        self.value = value
        self.payer_account = payer_account
        self.payee_account = payee_account
        self.oklistener = oklistener
        self.data()
        super().__init__(wallet.main_wnd, title=title, width=width, height=height)
        self.error.connect(self.errorSlot)

    @component.data
    def data(self):
        return {
            "password": ""
        }

    @QtCore.pyqtSlot(str)
    def errorSlot(self, err):
        QMessageBox.information(self, "Error", err)

    def send(self):
        passwd = self.password.value
        if web3.personal.unlockAccount(self.payer_account, passwd):
            web3.personal.lockAccount(self.payer_account)
        else:
            self.error.emit('wrong passphrase')
            return True
        transaction = {
            'from': self.payer_account,
            'to': self.payee_account,
            'value': self.value
        }
        web3.personal.sendTransaction(transaction, passwd)
        return False

    def beforeSend(self, _):
        def cb(err):
            self.setLoading(False)
            if not err:
                app.event.emit(UPDATE)
                self.close()
        self.setLoading(True)
        deferToThread(self.send).addCallback(cb)

    def setLoading(self, is_show):
        if is_show:
            self.loading.show()
            self.ok.setEnabled(False)
        else:
            self.loading.hide()
            self.ok.setEnabled(True)

    def ui(self, widget):
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        self.loading = Loading()
        layout.addLayout(self.gen_row('Payment password:', Input.Builder(
            height=25, width=225).mode(Input.Password).model(self.password).build(), left_width=120))
        layout.addLayout(self.gen_row('', self.loading, left_width=120))
        self.loading.hide()

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        self.ok = Button.Builder(width=100, height=28).style(
            'primary').click(self.beforeSend).text('OK').build()
        hbox.addWidget(self.ok)
        hbox.addSpacing(5)

        layout.addLayout(hbox)
        return layout

    def style(self):
        return super().style() + """
        
        """


class WalletPage(Page):

    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(parent)

        def update(_):
            self.balance.value = account.to_ether(account.get_balance(app.addr))
        app.event.register(UPDATE, update)

    def load_data(self, data):
        records = []
        for item in data:
            is_frm = app.addr == item['frm']
            amount = float(item['value'])
            records.append(Record(category='Transfer Out' if is_frm else 'Transfer',
                                  payer=app.username if is_frm or amount == 0 else item['frm'],
                                  amount=- amount if is_frm and amount != 0 else amount,
                                  time=dt.strptime(item['date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y/%m/%d %H:%M')))
        self.table_data.value = records
        if len(records) == 0:
            self.nodata.show()
        else:
            self.nodata.hide()

    @page.create
    def create(self):
        self.balance.value = account.to_ether(account.get_balance(app.addr))
        # Load records
        wallet.market_client.query_records(
            address=app.addr).addCallbacks(self.load_data)

    @page.data
    def data(self):
        return {
            'balance': 0,
            'table_data': []
        }

    def receive(self, _):
        receiveDlg = ReceiveDialog(address=app.addr)
        receiveDlg.show()

    def send(self, _):
        sendDlg = SendDialog(
            gas=10, account_amount=self.balance.value, address=app.addr)
        sendDlg.show()

    def ui(self, layout):
        layout.setAlignment(Qt.AlignTop)
        self.add(Builder().text('Balance').name('title').build())
        self.addH(Builder(Label).model(self.balance).name(
            'amount').build(), 0, align=Qt.AlignBottom | Qt.AlignLeft)
        self.addH(Builder().text('CPC').name('unit').build())

        self.add()
        width = 90
        height = 30
        self.addH(Button.Builder(width=width, height=height).text('Receive').click(
            self.receive).name('receive').style('primary').build())
        self.addH(Button.Builder(width=width, height=height).text(
            'Send').click(self.send).name('send').build())
        self.add(space=20)
        self.add(Line(wid=1, color='#e1e1e1'))
        self.add(space=18)
        self.add(Builder().text('Account').name('title').build())

        def buildTable():
            header = {
                'headers': ['Category', 'Payer', 'Amount(CPC)', 'Time'],
                'width': [202, 190, 170, 108]
            }
            data = []
            self.table_data.value = data

            def itemHandler(data):
                items = []
                items.append(data.category)
                items.append(data.payer)
                wid = QLabel(('+' if data.amount >= 0 else '') +
                             str(data.amount))
                wid.setStyleSheet("QLabel{{color: {};}}".format(
                    '#00a20e' if data.amount >= 0 else '#d0021b'))
                items.append(wid)
                items.append(data.time)
                return items

            table = Table(self, header, self.table_data,
                          itemHandler, sort=None)
            table.setObjectName('my_table')
            table.setFixedWidth(802)
            return table
        table = buildTable()
        self.table = table
        self.buildTable = buildTable

        self.add(table)

        # No Data
        nodata = QLabel('No Data!')
        nodata.setObjectName('no_data')
        self.nodata = nodata
        self.add(nodata)
        self.nodata.hide()
        if len(self.table_data.value) == 0:
            self.nodata.show()
        layout.addStretch(1)
        return layout

    def style(self):
        margin_left = 30
        return """
        QLabel#no_data {{
            color: #aaa;
            margin-left: 310px;
        }}
        QLabel#title {{
            font-size:24px;
            font-weight:500;
            margin-top: 20px;
            margin-left: {margin_left}px;
        }}
        QLabel#amount {{
            font-size:20px;
            margin-top: 30px;
            margin-left: {margin_left}px;
        }}
        QLabel#unit {{
            font-size:14px;
            margin-top: 35px;
        }}
        QPushButton#receive {{
            margin-top: 30px;
            margin-left: {margin_left}px;
        }}
        QPushButton#send {{
            margin-top: 30px;
            margin-left: 30px;
        }}
        """.format(margin_left=margin_left)
