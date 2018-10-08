
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QLabel

from cpchain.wallet import fs

from cpchain.wallet.components.table import Table
from cpchain.wallet.pages import wallet, app, abs_path, Binder
from cpchain.wallet.simpleqt import Page
from cpchain.wallet.simpleqt.decorator import page
from cpchain.utils import sizeof_fmt

from cpchain.wallet.simpleqt.basic import Builder, Button, Input, Line

logger = logging.getLogger(__name__)

class Record:
    category = "category"
    payer = "Ptest"
    amount = 100
    time = '2018/2/4  08:30'

    def __init__(self, *args, **kw):
        for k, v in kw.items():
            self.__dict__[k] = v


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
            'balance': 1000.00,
            'table_data': []
        }

    def ui(self, layout):
        layout.setAlignment(Qt.AlignTop)
        self.add(Builder().text('Balance').name('title').build())
        self.addH(Builder().text(self.balance.value).name('amount').build(), 0, align=Qt.AlignBottom | Qt.AlignLeft)
        self.addH(Builder().text('CPC').name('unit').build())

        self.add()
        width = 90
        height = 30
        self.addH(Button.Builder(width=width, height=height).text('Receive').name('receive').style('primary').build())
        self.addH(Button.Builder(width=width, height=height).text('Send').name('send').build())
        self.add(space=20)
        self.add(Line(wid=1, color='#e1e1e1'))
        self.add(space=18)
        self.add(Builder().text('Account').name('title').build())

        def buildTable():
            header = {
                'headers': ['Category', 'Payer', 'Amount(CPC)', 'Time'],
                'width': [252, 140, 170, 108]
            }
            data = [Record(), Record(amount=-100)]
            self.table_data.value = data
            def buildProductClickListener(product_id):
                def listener(event):
                    app.router.redirectTo('publish_product', product_id=product_id)
                return listener
            def itemHandler(data):
                items = []
                items.append(data.category)
                items.append(data.payer)
                wid = QLabel(('+' if data.amount > 0 else '') + str(data.amount))
                wid.setStyleSheet("QLabel{{color: {};}}".format('#00a20e' if data.amount > 0 else '#d0021b'))
                items.append(wid)
                items.append(data.time)
                return items

            table = Table(self, header, self.table_data, itemHandler, sort=None)
            table.setObjectName('my_table')
            table.setFixedWidth(802)
            if len(self.table_data.value) > 0:
                table.setMinimumHeight(180)
            else:
                table.setMaximumHeight(40)
            return table
        table = buildTable()
        self.table = table
        self.buildTable = buildTable

        self.add(table)

        if len(self.table_data.value) == 0:
            # No Data
            nodata = QLabel('No Data!')
            nodata.setObjectName('no_data')
            self.add(nodata)
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

