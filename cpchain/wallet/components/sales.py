from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap

from twisted.internet.threads import deferToThread
from twisted.internet.defer import inlineCallbacks, Deferred

from cpchain.wallet.pages import Binder, app, wallet
from cpchain.wallet.simpleqt.decorator import component

import traceback
import asyncio
import logging

logger = logging.getLogger(__name__)

class Status(QWidget):

    def __init__(self, name, mode=None, timestamp=None, line=True, h1=100, h2=20, width=100):
        """
        @param mode: finish, active, todo
        """
        self.name = name
        self.mode = mode
        self.timestamp = timestamp
        self.line = line
        self.h1 = h1
        self.h2 = h2
        self.width = width
        super().__init__()
        self.ui()

    def getColor(self):
        color = {
            'finish': '#333333',
            'active': '#0073df',
            'todo': '#9b9b9b'
        }
        if self.mode is None:
            return color['todo']
        return color[self.mode]

    def ui(self):
        miniWidth = self.width
        self.setMinimumWidth(miniWidth)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        status = QLabel(self.name)
        status.setObjectName('status')
        status.setAlignment(Qt.AlignCenter)
        status.setMinimumWidth(miniWidth)
        status.setMinimumHeight(self.h1)
        layout.addWidget(status)
        if self.timestamp:
            timestamp = QLabel(self.timestamp)
            timestamp.setObjectName('timestamp')
            timestamp.setAlignment(Qt.AlignCenter)
            timestamp.setMinimumWidth(miniWidth)
            timestamp.setMinimumHeight(self.h2)
            layout.addWidget(timestamp)
        layout.addStretch(1)
        self.setLayout(layout)
        self.setStyleSheet("""
                #status {{
                    padding: 6px 2px;
                    font-family: SFUIDisplay-Regular;
                    font-size: 12px;
                    color: {};
                    border: 1px solid #d0d0d0;
                    border-radius: 15px;
                    text-align: center;
                }}
                #timestamp {{
                    font-size: 10px;
                }}
        """.format(self.getColor()))

class StatusLine(QWidget):

    def __init__(self, h1, h2):
        self.h1 = h1
        self.h2 = h2
        super().__init__()
        self.ui()

    def ui(self):
        v2 = QVBoxLayout()
        line = QLabel('-')
        blank = QLabel(' ')
        line.setObjectName('line')
        blank.setObjectName('blank')
        line.setMinimumHeight(self.h1)
        blank.setMinimumHeight(self.h2)
        v2.addWidget(line)
        v2.addWidget(blank)
        self.setLayout(v2)
        self.setStyleSheet("""
            color: #9d9d9d;
        """)

class Operator:

    def buyer_confirm(self, order_id):
        logger.debug('Buyer Confirm Order: %s', str(order_id))
        def func2(_):
            logger.debug('Buyer Confirmed')
            app.update()
        deferToThread(wallet.chain_broker.buyer.confirm_order, order_id).addCallbacks(func2)

class Sale(QWidget):

    def __init__(self, image, name, current, timestamps, order_id=None):
        self.image = image
        self.name = name
        # currrent status index
        self.current = current
        # action's timestamp, a list
        self.timestamps = timestamps
        self.order_id = order_id
        self.operator = Operator()
        print(app.products_order)
        super().__init__()
        self.ui()

    def _deliver(self):
        wallet.chain_broker.seller.confirm_order(self.order_id)

    def deliver(self, _):
        def func(_):
            order_info = dict()
            order_info[self.order_id] = wallet.chain_broker.buyer.query_order(self.order_id)
            wallet.chain_broker.seller_send_request(order_info)
        deferToThread(self._deliver).addCallbacks(func)

    @inlineCallbacks
    def _receive(self):
        order_info = dict()
        order_info[self.order_id] = yield wallet.chain_broker.buyer.query_order(self.order_id)
        yield wallet.chain_broker.buyer_send_request(order_info)

    def receive(self, _):
        self._receive()

    def confirm(self, _):
        self.operator.buyer_confirm(self.order_id)


    def ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        first = QHBoxLayout()
        image = QLabel()
        image.setObjectName('image')
        pix = QPixmap(self.image)
        pix = pix.scaled(48, 48)
        image.setPixmap(pix)
        first.addWidget(image)

        name = QLabel(self.name)
        first.addWidget(name)
        first.addStretch(1)
        layout.addLayout(first)

        status = [
            'Order',
            'Deliver',
            'Receive',
            'Confirm',
            # 'Comment'
        ]
        callbacks = {
            'Deliver': self.deliver,
            'Receive': self.receive,
            'Confirm': self.confirm
        }
        second = QHBoxLayout()
        second.setAlignment(Qt.AlignLeft)
        i = 0
        h1 = 35
        h2 = 15
        width = 78
        for item in status:
            mode = 'active' if i == self.current else ('todo' if i > self.current else 'finish')
            timestamp = self.timestamps[i] if i < self.current else None
            tmp = Status(name=item,
                         mode=mode,
                         timestamp=timestamp,
                         h1=h1,
                         h2=h2,
                         width=width)
            cb = callbacks.get(item)
            if cb and mode == 'active':
                Binder.click(tmp, cb)
            second.addWidget(tmp)
            if item != status[-1]:
                line = StatusLine(h1, h2)
                second.addWidget(line)
            i += 1
        second.addStretch(1)
        layout.addLayout(second)
        layout.addStretch(1)
        self.setLayout(layout)
        self.setStyleSheet("""
        """)
