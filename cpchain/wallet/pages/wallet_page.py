
import logging
import time
import webbrowser
from datetime import datetime as dt

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMessageBox,
                             QVBoxLayout, QWidget, QFrame)
from twisted.internet.threads import deferToThread

from cpchain import account
from cpchain.chain.utils import default_w3 as web3
from cpchain.utils import config
from cpchain.wallet import utils
from cpchain.wallet.components.dialog import Dialog
from cpchain.wallet.components.loading import Loading
from cpchain.wallet.components.table import Table
from cpchain.wallet.components.picture import Picture
from cpchain.wallet.pages import app, wallet, abs_path
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
        width = 580
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

    def show_copied(self):
        self.copied.show()

    def copy_address(self, _):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.address.value)
        self.show_copied()

    def openUrl(self, url):
        try:
            webbrowser.get('chrome').open_new_tab(url)
        except:
            webbrowser.open_new_tab(url)

    def ui(self, widget):
        layout = QVBoxLayout(widget)
        row = QHBoxLayout()
        row.setSpacing(0)
        row.addWidget(Builder().text('Address:').name('address_hint').build())
        row.addWidget(Builder().text(self.address.value).name('address').build())
        row.addSpacing(10)
        picture = Picture(abs_path('icons/copy@2x.png'), width=30, height=30)
        picture.setObjectName('picture')
        row.addWidget(picture)
        row.addSpacing(8)
        row.addWidget(Builder().click(self.copy_address).text('Copy').name('copy').build())
        row.addStretch(1)
        layout.addLayout(row)
        row2 = QHBoxLayout()
        row2.setSpacing(0)
        row2.addSpacing(15)
        row2.setAlignment(Qt.AlignBottom)
        qrcode = Picture(utils.get_cpc_free_qrcode(), width=96, height=96)
        qrcode.setObjectName('qrcode')
        row2.addWidget(qrcode)
        row2.addSpacing(10)

        copied_icon = Picture(abs_path('icons/copied@2x.png'), width=30, height=30)
        copied_layout = QHBoxLayout()
        copied_layout.setContentsMargins(0, 0, 0, 0)
        copied_layout.setSpacing(0)
        copied_layout.addWidget(copied_icon)
        copied_text = Builder().text('copied!').name('copied').build()
        copied_layout.addWidget(copied_text)
        copied_layout.addStretch(1)
        self.copied = QFrame(self)
        self.copied.setObjectName('copied_frame')
        self.copied.setLayout(copied_layout)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setAlignment(Qt.AlignTop)
        vbox.addWidget(self.copied)

        row2.addLayout(vbox)
        self.copied.hide()
        row2.addStretch(1)
        layout.addLayout(row2)
        layout.addWidget(Builder().text('Get CPC for free').name('get_cpc').click(
            lambda _: self.openUrl(config.account.charge_server)).build())
        return layout

    def style(self):
        return super().style() + """
        QLabel {
            font-size:15px;
        }
        QLabel#address_hint {
            font-weight: 700;
            margin-left: 15px;
        }
        QLabel#address {
            font-weight: 500;
        }
        QLabel#get_cpc {
            margin-top: 10px;
            color:#0073df;
            font-size: 12px;
            margin-left: 15px;
        }
        QLabel#copy {
            color: #0073DF;
        }
        QLabel#copied {
            margin-left: 3px;
            color: #aaa;
            font-size: 12px;
        }
        QFrame#copied_frame {
            /*margin-bottom: 45px;*/
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

    def gen_row(self, left_text, *widgets, **kw):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addSpacing(16)
        left_widget = Builder().text(left_text).name('left').build()
        width = kw.get('left_width', 130)
        left_widget.setMinimumWidth(width)
        left_widget.setMaximumWidth(width)
        row.addWidget(left_widget)
        for widget in widgets:
            if isinstance(widget, QWidget):
                row.addWidget(widget)
                row.addSpacing(5)
        row.addStretch(1)
        return row

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
        cancel = Button.Builder(width=100, height=28).click(
            lambda _: self.close()).text('Cancel').build()
        hbox.addWidget(cancel)
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
            color: #333333;
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
        value = account.to_wei(self.value)
        transaction = {
            'from': self.payer_account,
            'to': self.payee_account,
            'value': value
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

    def gen_row(self, left_text, *widgets, **kw):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addSpacing(16)
        left_widget = Builder().text(left_text).name('left').build()
        width = kw.get('left_width', 130)
        left_widget.setMinimumWidth(width)
        left_widget.setMaximumWidth(width)
        row.addWidget(left_widget)
        for widget in widgets:
            if isinstance(widget, QWidget):
                row.addWidget(widget)
                row.addSpacing(5)
        row.addStretch(1)
        return row

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

    loaded = pyqtSignal(list)

    def __init__(self, parent=None):
        logger.debug('Wallet Page')
        self.parent = parent
        self.nodata = None
        super().__init__(parent)

        def update(_):
            self.balance.value = account.to_ether(account.get_balance(app.addr))
        app.event.register(UPDATE, update)
        self.loaded.connect(self.loadedSlot)
        self.load()
        logger.debug('inited')

    def loadedSlot(self, records):
        logger.debug('load records')
        if self.nodata:
            if len(records) == 0:
                self.nodata.show()
            else:
                self.nodata.hide()
        logger.debug('render table')
        self.table_data.value = records
        logger.debug('rendered table')
        logger.debug('loaded')

    def loaded_data(self, data):
        logger.debug('load data')
        records = []
        for item in data:
            is_frm = app.addr == item['frm']
            amount = float(item['value'])
            username = app.username or ""
            records.append(Record(category='Transfer Out' if is_frm else 'Transfer',
                                  payer=username if is_frm or amount == 0 else item['frm'],
                                  amount=- amount if is_frm and amount != 0 else amount,
                                  time=dt.strptime(item['date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y/%m/%d %H:%M')))
        self.loaded.emit(records)

    @page.create
    def load(self):
        logger.debug('create')
        self.balance.value = account.to_ether(account.get_balance(app.addr))
        logger.debug('get balance')
        # Load records
        wallet.market_client.query_records(
            address=app.addr).addCallbacks(self.loaded_data)
        logger.debug('query records')

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
