#!/usr/bin/python3

import json
import logging
import os
import shelve
import sys
import time
import random
import string
from threading import Thread

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication,
                             QDesktopWidget, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
                             QMainWindow, QProgressBar,
                             QPushButton, QRadioButton, QScrollArea,
                             QVBoxLayout, QWidget)
from twisted.internet.task import LoopingCall
from twisted.logger import globalLogBeginner, textFileLogObserver
from twisted.web import client

import sha3
from cpchain.account import Account
from cpchain.chain.utils import default_w3 as web3
from cpchain.crypto import ECCipher, RSACipher
from cpchain.storage_plugin import ipfs, proxy, s3, stream, template
from cpchain.utils import reactor, config

from cpchain.wallet import events, utils
# widgets
from cpchain.wallet.components.sidebar import SideBar
from cpchain.wallet.pages import app, load_stylesheet, main_wnd, wallet, abs_path
from cpchain.wallet.pages.header import Header
from cpchain.wallet.pages.login import LoginWindow
from cpchain.wallet.router import Router
from cpchain.wallet.simpleqt import MessageBox, event

client._HTTP11ClientFactory.noisy = False

globalLogBeginner.beginLoggingTo([textFileLogObserver(sys.stdout)])
logger = logging.getLogger(__name__)

_Application = QApplication(sys.argv)

# load fonts
utils.load_fonts(abs_path('fonts'))
font = QFont('SF UI Display')
_Application.setFont(font)


sidebarMenu = [
    {
        'name': 'Wallet',
        'icon': 'wallet@2x.png',
        'link': 'wallet'
    },
    {
        'name': 'Home',
        'icon': 'home@2x.png',
        'link': 'home'
    },
    {
        'name': 'Market',
        'icon': 'market@2x.png',
        'link': 'market_page'
    }, {
        'name': 'My Data',
        'icon': 'my data@2x.png',
        'link': 'my_data_tab'
    }, {
        'name': 'Purchased Data',
        'icon': 'purchased data@2x.png',
        'link': 'purchased_page'
    }
]

class MainWindow(QMainWindow):

    def search_handler(self, val):
        app.router.redirectTo('market_page', search=val)

    search_signal = QtCore.pyqtSignal(str, name="modelChanged")

    def __init__(self, reactor):
        super().__init__()
        self.reactor = reactor
        self.body = None
        self.search_signal.connect(self.search_handler)
        self.init_ui()
        self.content_tabs = None


    def init_ui(self):
        self.setWindowTitle('CPChain Wallet')
        self.setObjectName("main_window")
        self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setWindowOpacity(1)
        self.main_tab_index = {}

        def set_geometry():
            self.resize(1002, 710)  # resize before centering.
            self.setMinimumSize(800, 500)
            center_pt = QDesktopWidget().availableGeometry().center()
            qrect = self.frameGeometry()
            qrect.moveCenter(center_pt)
            self.move(qrect.topLeft())
        set_geometry()

        header = Header(self)
        header.setObjectName('header')
        header.setMinimumHeight(100)
        sidebar = SideBar(sidebarMenu)

        def set_layout():
            main_layout = QVBoxLayout()
            main_layout.setSpacing(0)
            main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addWidget(header)

            content_layout = QHBoxLayout()
            content_layout.setSpacing(0)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.addWidget(sidebar)
            self.body = QWidget()
            self.body.setContentsMargins(0, 0, 0, 0)
            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(Router.index(self.body))
            self.body.setLayout(layout)
            self.body.setMinimumWidth(803)
            # self.body.setMaximumWidth(803)
            self.body.setMinimumHeight(633)
            # self.body.setMaximumHeight(633)
            content_layout.addStretch(1)
            content_layout.addWidget(self.body)
            content_layout.addStretch(1)
            main_layout.addLayout(content_layout)
            wid = QWidget(self)
            wid.setLayout(main_layout)
            self.setCentralWidget(wid)
        set_layout()
        load_stylesheet(self, "main_window.qss")

        self.show()


    def closeEvent(self, _):
        self.reactor.stop()
        os._exit(0)

def _handle_keyboard_interrupt():
    def sigint_handler(*args):
        # _Application.quit()
        pass

    import signal
    signal.signal(signal.SIGINT, sigint_handler)

    from PyQt5.QtCore import QTimer

    _handle_keyboard_interrupt.timer = QTimer()
    timer = _handle_keyboard_interrupt.timer
    timer.start(300)
    timer.timeout.connect(lambda: None)

def __unlock():
    try:
        web3.personal.unlockAccount(app.addr, app.pwd)
    except Exception as e:
        logger.exception(e)

def valid_password(password):
    path = os.path.expanduser('~/.cpchain')
    with shelve.open(os.path.join(path, 'account')) as file:
        key_path = file.get('key_path')
        with open(key_path) as f:
            encrypted_key = json.load(f)
        try:
            web3.eth.account.decrypt(encrypted_key, password)
            return True
        except ValueError as e:
            logger.exception(e)
            event.emit(events.PASSWORD_ERROR)
            return False


def initialize_system():
    if hasattr(wallet, 'chain_broker'):
        update = LoopingCall(app.update)
        update.start(5)


def buildMainWnd():
    main_wnd = MainWindow(reactor)
    _handle_keyboard_interrupt()
    return main_wnd


def __login(account=None):
    if account is None:
        wallet.accounts.set_default_account(1)
        account = wallet.accounts.default_account
    public_key = ECCipher.serialize_public_key(account.public_key)
    addr = utils.get_address_from_public_key_object(public_key)
    addr = web3.toChecksumAddress(addr)
    app.addr = addr
    if isinstance(account.key_passphrase, str):
        app.pwd = account.key_passphrase
    else:
        app.pwd = account.key_passphrase.decode()
    wallet.market_client.account = account
    wallet.market_client.public_key = ECCipher.serialize_public_key(wallet.market_client.account.public_key)
    wallet.market_client.login(app.username).addCallbacks(lambda _: event.emit(events.LOGIN_COMPLETED))
    wallet.init()
    initialize_system()
    app.router.redirectTo('market_page')

def enterPDash(account=None):
    if app.main_wnd:
        __login(account)
        return
    app.router = Router
    main_wnd = buildMainWnd()
    QtWidgets.qApp.setApplicationDisplayName('PDash')

    app.main_wnd = main_wnd

    wallet.set_main_wnd(main_wnd)
    app.timing(logger, 'Build MainWnd')
    __login(account)


def login():
    path = os.path.expanduser('~/.cpchain')
    if not os.path.exists(path):
        os.mkdir(path)
    with shelve.open(os.path.join(path, 'account')) as file:
        key_path = file.get('key_path')
        key_passphrase = file.get('key_passphrase')
        try:
            app.timing(logger, 'Data Init')
            if key_path and key_passphrase:
                if isinstance(key_passphrase, str):
                    account = Account(key_path, key_passphrase.encode())
                else:
                    account = Account(key_path, key_passphrase)
                public_key = ECCipher.serialize_public_key(account.public_key)
                # Init market client account
                wallet.market_client.account = account
                wallet.market_client.public_key = public_key
                app.timing(logger, 'Account Prepare')
                addr = utils.get_address_from_public_key_object(public_key)
                addr = web3.toChecksumAddress(addr)
                logger.info(addr)
                app.addr = addr
                if isinstance(key_passphrase, str):
                    app.pwd = key_passphrase
                else:
                    app.pwd = key_passphrase.decode()
                wallet.market_client.query_username(app)
                __unlock()
                app.timing(logger, 'Unlock')
                enterPDash(account)
                return
        except Exception as e:
            logger.error(e)
    logger.debug('Init')
    wnd = LoginWindow(reactor)
    wnd.show()
    wallet.set_main_wnd(wnd)

def save_login_info():
    path = os.path.expanduser('~/.cpchain')
    if not os.path.exists(path):
        os.mkdir(path)
    with shelve.open(os.path.join(path, 'account')) as file:
        file['key_path'] = wallet.market_client.account.key_path
        file['key_passphrase'] = wallet.market_client.account.key_passphrase


def search(event):
    search = event.data
    wallet.main_wnd.search_signal.emit(search)


def init_handlers():
    event.register(events.LOGIN_COMPLETED, lambda _: save_login_info())
    event.register(events.SEARCH, search)


def create_rsa_key():
    path = os.path.expanduser('~/.cpchain')
    password_file = path + '/password'
    key_file = path + '/private_key.pem'
    config.conf['wallet']['rsa_private_key_password_file'] = password_file
    config.conf['wallet']['rsa_private_key_file'] = key_file
    # if private.pem
    if not os.path.exists(password_file) or not os.path.exists(key_file):
        salt = ''.join(random.sample(string.ascii_letters + string.digits, 20))
        RSACipher.generate_private_key(password=salt.encode())

if __name__ == '__main__':
    app.start_at = time.time()
    app.unlock = __unlock
    app.valid_password = valid_password
    wallet.app = app
    app.enterPDash = enterPDash
    init_handlers()
    app.timing(logger, 'Init')

    login()

    app.timing(logger, 'Login')

    create_rsa_key()
    app.timing(logger, 'Create rsa_key')

    app.msgbox = MessageBox()
    app.msgbox.parent = app.main_wnd
    app.msgbox1 = MessageBox

    Thread(target=reactor.run, args=(False,)).start()

    sys.exit(_Application.exec_())
