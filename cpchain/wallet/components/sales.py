import asyncio
import logging
import traceback

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from PyQt5.QtQuickWidgets import QQuickWidget
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.threads import deferToThread

from cpchain.wallet import utils
from cpchain.wallet.components.gif import LoadingGif
from cpchain.wallet.components.loading import Loading
from cpchain.wallet.pages import Binder, app, wallet, HorizontalLine, qml_path
from cpchain.wallet.simpleqt import Signals
from cpchain.wallet.simpleqt.model import Model
from cpchain.wallet.simpleqt.basic import Builder
from cpchain.wallet.simpleqt.decorator import component

from .comment import CommentDialog

logger = logging.getLogger(__name__)


class Status(QWidget):

    def __init__(self, name, mode=None, timestamp=None, line=True, h1=100,
                 h2=20, width=100, status=False, order_id=None):
        """
        @param mode: finish, active, todo
        """
        self.signals = Signals()
        self.name = name
        self.order_id = order_id
        self.mode = mode
        self.timestamp = timestamp
        self.line = line
        self.h1 = h1
        self.h2 = h2
        self.status = status
        self.width = width
        self.status_elem = None
        super().__init__()
        self.init()
        self.ui()

    def init(self):
        @app.event.register(app.events.UPDATE_ORDER_STATUS)
        def callback(event):
            order_id = event.data['order_id']
            if order_id != self.order_id:
                return
            status = event.data['status']
            tmp_map = {
                'Deliver': ('delivering', 'delivery'),
                'Receive': ('receiving', 'receive'),
                'Confirm': ('confirming', 'confirm')
            }
            for k, v in tmp_map.items():
                if self.name == k:
                    if status == v[0]:
                        self.signals.loading.emit()
                    elif status == v[1]:
                        self.signals.loading_over.emit()
        self.signals.loading.connect(self.setLoading)
        self.signals.loading_over.connect(self.hideLoading)

    @pyqtSlot()
    def setLoading(self):
        self.setEnabled(False)
        self.loading.show()

    @pyqtSlot()
    def hideLoading(self):
        self.setEnabled(True)
        self.loading.hide()

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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignTop)
        status = QLabel(self.name)
        status.setObjectName('status')
        status.setAlignment(Qt.AlignCenter)
        status.setMinimumWidth(miniWidth)
        status.setMinimumHeight(self.h1)
        layout.addWidget(status)
        self.status_elem = status
        if self.timestamp:
            timestamp = QLabel(self.timestamp)
            timestamp.setObjectName('timestamp')
            timestamp.setAlignment(Qt.AlignCenter)
            timestamp.setMinimumWidth(miniWidth)
            timestamp.setMinimumHeight(self.h2)
            layout.addWidget(timestamp)
        self.loading = Loading(width=11, height=11, font_size=11)
        self.loading.setObjectName('loading')
        self.loading.setMaximumHeight(self.h2)
        self.loading.setMinimumHeight(self.h2)
        self.loading.setMaximumWidth(miniWidth)
        self.loading.hide()
        layout.addWidget(self.loading)
        layout.addStretch(1)
        self.setLayout(layout)
        self.setStyleSheet("""
                #status {{
                    padding: 6px 2px;
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
        v2.setContentsMargins(0, 0, 0, 0)
        # line = QLabel('-')
        line = HorizontalLine(wid=1, color="#9d9d9d")
        blank = QLabel(' ')
        line.setObjectName('line')
        blank.setObjectName('blank')
        line.setMinimumWidth(20)
        line.setMinimumHeight(self.h1)
        blank.setMinimumHeight(self.h2)
        v2.addWidget(line)
        v2.addWidget(blank)
        self.setLayout(v2)
        self.setStyleSheet("""
            color: #9d9d9d;
            margin-top: {}px;
        """.format(int(self.h1/2)))


class Operator:

    order_id = False

    def buyer_confirm(self, order_id):
        self.order_id = order_id
        app.event.emit(app.events.UPDATE_ORDER_STATUS, {
            'order_id': order_id, 'status': 'confirming'})

        def exec_():
            app.unlock()
            logger.debug('Buyer Confirm Order: %s', str(order_id))

            def func2(_):
                logger.debug('Buyer Confirmed')
                app.event.emit(app.events.BUYER_CONFIRM, order_id)
            deferToThread(wallet.chain_broker.buyer.confirm_order,
                          order_id).addCallbacks(func2)
        deferToThread(exec_)


class Sale(QWidget):

    def __init__(self, image, name, current, timestamps, order_id=None, mhash=None,
                 is_buyer=False, is_seller=False, order_type='file'):
        self.image = image
        self.address = name
        if not name:
            name = ""
        self.name = Model('...')
        # currrent status index
        self.current = current
        # action's timestamp, a list
        self.timestamps = timestamps
        self.order_id = order_id
        self.mhash = mhash
        self.comment_opened = False
        self.is_buyer = is_buyer
        self.is_seller = is_seller
        self.order_type = order_type
        self.operator = Operator()
        super().__init__()
        self.init()
        self.ui()
        deferToThread(self.get_username)

    def get_username(self):
        key = utils.eth_addr_to_string(self.address)
        def cb(r):
            self.name.value = r['username']
        wallet.market_client.query_username(public_key=key).addCallbacks(cb)

    def init(self):
        @app.event.register(app.events.SELLER_DELIVERY)
        def listenDeliver(event):
            if event.data == self.order_id:
                app.event.emit(app.events.UPDATE_ORDER_STATUS, {
                    'order_id': self.order_id, 'status': 'delivery'})

        @app.event.register(app.events.BUYER_RECEIVE)
        def listenDeliver(event):
            if event.data == self.order_id:
                app.event.emit(app.events.UPDATE_ORDER_STATUS, {
                    'order_id': self.order_id, 'status': 'receive'})

        @app.event.register(app.events.BUYER_CONFIRM)
        def listenDeliver(event):
            if event.data == self.order_id:
                app.event.emit(app.events.UPDATE_ORDER_STATUS, {
                    'order_id': self.order_id, 'status': 'confirm'})

    def _deliver(self):
        app.unlock()
        wallet.chain_broker.seller.confirm_order(self.order_id)

    def deliver(self, _):
        def func(_):
            order_info = dict()
            order_info[self.order_id] = wallet.chain_broker.buyer.query_order(
                self.order_id)
            app.unlock()
            if self.order_type == 'file':
                wallet.chain_broker.seller_send_request(order_info)
            else:
                wallet.chain_broker.seller_send_request_stream(order_info)
        deferToThread(self._deliver).addCallbacks(func)
        app.event.emit(app.events.UPDATE_ORDER_STATUS, {
            'order_id': self.order_id, 'status': 'delivering'})

    @inlineCallbacks
    def _receive(self):
        order_info = dict()
        order_info[self.order_id] = wallet.chain_broker.buyer.query_order(
            self.order_id)
        if self.order_type == 'file':
            yield wallet.chain_broker.buyer_send_request(order_info)
        else:
            yield wallet.chain_broker.buyer_send_request_stream(order_info)

    def receive(self, _):
        app.event.emit(app.events.UPDATE_ORDER_STATUS, {
            'order_id': self.order_id, 'status': 'receiving'})

        def unlock():
            app.unlock()
        deferToThread(unlock).addCallback(lambda _: self._receive())

    def confirm(self, _):
        self.operator.buyer_confirm(self.order_id)

    def comment(self, _):
        if self.comment_opened:
            return
        self.comment_opened = True
        comment = CommentDialog()
        comment.exec_()
        self.comment_opened = False

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

        name = Builder().model(self.name).build()
        first.addWidget(name)
        first.addStretch(1)
        layout.addLayout(first)

        status = [
            'Order',
            'Deliver',
            'Receive',
            'Confirm',
            'Comment'
        ]
        callbacks = {
            'Deliver': self.deliver,
            'Receive': self.receive,
            'Confirm': self.confirm,
            'Comment': self.comment
        }
        second = QHBoxLayout()
        second.setAlignment(Qt.AlignLeft)
        second.addSpacing(50)
        second.setSpacing(5)
        i = 0
        h1 = 35
        h2 = 15
        width = 95
        for item in status:
            mode = 'active' if i == self.current else (
                'todo' if i > self.current else 'finish')
            if item == 'Deliver' and self.current == 1 and self.is_buyer:
                mode = 'todo'
            if item == 'Receive' and self.current == 2 and self.is_seller:
                mode = 'todo'
            if item == 'Confirm' and self.current == 3 and self.is_seller:
                mode = 'todo'
            if item == 'Comment' and self.current == 4 and self.is_seller:
                mode = 'todo'
            timestamp = self.timestamps[i] if i < self.current else None
            tmp = Status(name=item,
                         mode=mode,
                         timestamp=timestamp,
                         h1=h1,
                         h2=h2,
                         width=width,
                         order_id=self.order_id)
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
