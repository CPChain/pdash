import logging
import os
import shutil
from datetime import datetime as dt

from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QPixmap
from PyQt5.QtWidgets import (QDesktopWidget, QFileDialog, QHBoxLayout,
                             QMainWindow, QMessageBox, QPushButton,
                             QVBoxLayout, QWidget)
from twisted.internet.threads import deferToThread

from cpchain.account import create_account, import_account
from cpchain.crypto import ECCipher
from cpchain.wallet.components.agreement import Agreement
from cpchain.wallet.components.gif import LoadingGif
from cpchain.wallet.components.loading import Loading
from cpchain.wallet.components.upload import FileUpload
from cpchain.wallet.pages import abs_path, app, wallet
from cpchain.wallet.simpleqt import Model, validate
from cpchain.wallet.simpleqt.basic import Builder, Button, Input

logger = logging.getLogger(__name__)


class MyWindow(QMainWindow):

    def __init__(self, reactor=None, parent=None):
        self._endPos = None
        self._isTracking = None
        self._startPos = None
        super().__init__()
        self.reactor = reactor
        self.parent = parent
        if app.main_wnd:
            app.main_wnd.mouseReleaseEvent = lambda _: app.event.emit(app.events.LOGIN_CLOSE)
        self.init()
        main = self.__ui()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.ui(self.layout)
        main.addLayout(self.layout)
        __style = self.__style()
        style = self.style()
        self.setStyleSheet(__style + style)

    def close(self):
        if self.parent:
            self.parent.show()
            self.hide()
        else:
            app.event.emit(app.events.LOGIN_CLOSE)
            if app.main_wnd:
                app.main_wnd.mouseReleaseEvent = None
            super().close()

    def to(self, wnd):
        self.hide()
        wnd.show()

    def init(self):
        self.setWindowTitle('CPChain Wallet')
        self.setObjectName("main_window")
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.resize(350, 500)  # resize before centering.
        self.setMinimumSize(350, 500)
        center_pt = QDesktopWidget().availableGeometry().center()
        qrect = self.frameGeometry()
        qrect.moveCenter(center_pt)
        self.move(qrect.topLeft())

        self.setWindowTitle('CPChain Wallet')
        self.setObjectName("main_window")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAcceptDrops(True)

    def mouseMoveEvent(self, e: QMouseEvent):
        self._endPos = e.pos() - self._startPos
        self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

    def __ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        main_layout.setContentsMargins(0, 0, 0, 0)
        close_btn = Builder(widget=QPushButton).text(
            'x').name('close_btn').click(self.close).build()

        header = QHBoxLayout()
        header.addStretch(1)
        header.addWidget(close_btn)

        main_layout.addLayout(header)
        wid = QWidget(self)
        wid.setObjectName('main')
        wid.setLayout(main_layout)
        self.setCentralWidget(wid)
        return main_layout

    def __style(self):
        return """
            QMainWindow, QWidget#main {
                background:#f8f8f8;
                border:1px solid #cccccc;
                /*border-radius:5px;*/
            }
            QPushButton#close_btn {
                color: #d0021b;
                border: none;
                font-size: 18px;
                margin-top: 7px;
                margin-right: 15px;
            }

            QPushButton#close_btn:hover {
                color: #d1021b;
            }

            QPushButton#close_btn:pressed {
                color: #d2021b;
            }

            QLabel#title {
                font-size:20px;
                color:#222222;
                text-align:left;
            }
            QLabel#desc {
                font-size:13px;
                color:#222222;
                text-align:left;
            }
            QLabel#next {
                font-size:15px;
                color:#0073df;
            }
        """

    def closeEvent(self, _):
        if self.reactor:
            self.reactor.stop()
            os._exit(0)

    def style(self):
        return ""

    def ui(self, layout):
        pass

    def add(self, elem, space=None):
        if isinstance(elem, QWidget):
            self.layout.addWidget(elem)
        else:
            self.layout.addLayout(elem)
        if space:
            self.spacing(space)

    def spacing(self, space):
        self.layout.addSpacing(space)


class GeneratingWindow(MyWindow):

    def __init__(self, reactor, parent=None):
        super().__init__(reactor, parent)

    def ok(self):
        self.close()

    def ui(self, layout):
        self.spacing(40)
        title = Builder().text('Generating keystore file…')\
                         .name('title')\
                         .build()
        self.add(title)
        self.spacing(60)
        loading = LoadingGif(path=abs_path(
            'icons/GIF_3dot.gif'), width=228, height=228)
        self.add(loading)


class UserNameWindow(MyWindow):

    def __init__(self, reactor, parent):
        self.account = None
        self.is_registered_ = False
        self.username_ = ""
        self.username = Model("")
        super().__init__(reactor, parent)

    def enter(self):
        if not validate(self, lambda x: x, 'Please input username', self.username.value) or \
                not validate(self, lambda x: x, 'No Account!', self.account):
            return
        self.hide()
        app.username = self.username.value
        app.event.emit(app.events.LOGIN_CLOSE)
        app.enterPDash(self.account)

    @property
    def is_registered(self):
        return self.is_registered_

    @is_registered.setter
    def is_registered(self, val):
        self.is_registered_ = val
        if self.username_:
            self.username_elem.setEnabled(False)
            self.username.value = self.username_

    def ui(self, layout):
        title = Builder().text('Create a username')\
                         .name('title')\
                         .build()
        desc = Builder().text('The username will be bound to the keystore file and cannot be modified.')\
                        .name('desc')\
                        .wrap(True)\
                        .height(80)\
                        .build()
        self.add(title)
        self.add(desc, 40)
        username = Input.Builder().placeholder('Username')\
                                  .name('pwd')\
                                  .model(self.username)\
                                  .build()
        self.username_elem = username
        self.add(username, 10)
        self.add(Button.Builder().text('Enter PDash')
                 .style('primary')
                 .click(lambda _: self.enter())
                 .build())

    def style(self):
        return ""


class BackupWindow(MyWindow):

    def __init__(self, reactor, parent, path, next_):
        self.path = path
        self.next_ = next_
        super().__init__(reactor, parent)

    def backup(self):
        select_path = QFileDialog.getExistingDirectory()
        name = self.path.split('/')[-1]
        shutil.copyfile(self.path, select_path + '/' + name)
        QMessageBox.information(self, "Success", "Successful!")

    def ui(self, layout):
        title = Builder().text('Backup your wallet now')\
                         .name('title')\
                         .build()
        desc = Builder().text('Make sure you backup your keystore file and password.\n\n'
                              'Keep a copy of the keystore file where you can\'t lose it.')\
                        .name('desc')\
                        .wrap(True)\
                        .height(100)\
                        .build()
        self.add(title, 10)
        self.add(desc, 70)
        self.add(Button.Builder()
                 .text('Check and Backup')
                 .style('primary')
                 .click(lambda _: self.backup())
                 .build(), 10)
        self.add(Builder().name('next')
                 .text('Next >')
                 .align(Qt.AlignRight)
                 .click(lambda _: self.to(self.next_))
                 .build(), 10)


class CreateWindow(MyWindow):

    created = pyqtSignal()

    def __init__(self, reactor=None, parent=None):
        self.password = Model("")
        self.repeat = Model("")
        self.check = Model(False)
        self.PATH = os.path.expanduser('~/.cpchain/keystore')
        if not os.path.exists(self.PATH):
            os.mkdir(self.PATH)
        self.NAME = 'pdash-account-' + dt.now().strftime('%Y-%m-%d %H:%M:%S')
        super().__init__(reactor, parent)
        self.loading = GeneratingWindow(reactor, self)
        self.username = UserNameWindow(reactor, self)
        self.backup = BackupWindow(
            reactor, self, self.PATH + '/' + self.NAME, self.username)
        self.created.connect(self._after)

    def _after(self):
        self.loading.to(self.backup)

    def create(self):
        # Create Keystore
        if not validate(self, lambda x: x, "Please input password", self.password.value):
            return
        if not validate(self, lambda x: x, "Please repeat password", self.repeat.value):
            return
        if not validate(self, lambda x, y: x == y, "The passwords do not match", self.password.value, self.repeat.value):
            return
        if not validate(self, lambda x: x is True, "You haven't agreed to the agreement", self.check.value):
            return

        def _create():
            self.username.account = create_account(
                self.password.value, self.PATH, self.NAME)
        deferToThread(_create).addCallback(lambda _: self.created.emit())
        self.to(self.loading)

    def ui(self, layout):
        title = Builder().text('Create a new account')\
                         .name('title')\
                         .build()
        desc = Builder().text('The password cannot be modified and we cannot recover it, please backup cautiously.')\
                        .name('desc')\
                        .wrap(True)\
                        .height(80)\
                        .build()
        self.add(title)
        self.add(desc, 40)
        password = Input.Builder().placeholder('Password')\
                                  .name('pwd')\
                                  .mode(Input.Password)\
                                  .model(self.password)\
                                  .build()
        self.add(password, 10)
        repeat = Input.Builder().placeholder('Repeat Password')\
                                .name('repeat')\
                                .mode(Input.Password)\
                                .model(self.repeat)\
                                .build()
        self.add(repeat, 10)
        self.add(Agreement(self.check, width=228, height=30), 40)
        self.add(Button.Builder().text('Create')
                 .style('primary')
                 .click(lambda _: self.create())
                 .build())

    def style(self):
        return """ """


class ImportWindow(MyWindow):

    error_signal = pyqtSignal()

    imported = pyqtSignal(str)

    def __init__(self, reactor=None, parent=None):
        self.password = Model("")
        self.file = None
        super().__init__(reactor, parent)
        self.username = UserNameWindow(reactor, self)
        self.error_signal.connect(lambda: app.msgbox.error("Password mismatch"))
        self.imported.connect(self.onImported)
        @app.event.register(app.events.PASSWORD_ERROR)
        def password_error(_):
            self.loading_over()
            self.error_signal.emit()

    def onImported(self, status):
        self.username.username_ = status
        self.username.is_registered = True
        self.loading_over()
        self.to(self.username)

    def _import(self):
        self.loading_start()
        if not validate(self, lambda x: x, "Please input the password", self.password.value):
            self.loading_over()
            return
        if not validate(self, lambda x: x, "Please select a file", self.file.file):
            self.loading_over()
            return
        try:
            def exec_():
                account = import_account(self.file.file, self.password.value)
                self.username.account = account
                def cb(status):
                    self.imported.emit(status)
                if account:
                    public_key = ECCipher.serialize_public_key(account.public_key)
                    wallet.market_client.isRegistered(public_key).addCallbacks(cb)
            deferToThread(exec_)
        except Exception as e:
            logger.error(e)
            QMessageBox.information(self, "error", "Failed!")
            self.loading_over()

    def loading_start(self):
        self.import_.setEnabled(False)
        self.loading.show()

    def loading_over(self):
        self.import_.setEnabled(True)
        self.loading.hide()

    def ui(self, layout):
        title = Builder().text('Import a keystore file')\
                         .name('title')\
                         .build()
        desc = Builder().text('CPC Wallet uses a keystore format to store encrypted'
                              ' private key information, please drop the file below.')\
                        .name('desc')\
                        .wrap(True)\
                        .height(100)\
                        .build()
        self.add(title)
        self.add(desc, 25)
        self.file = FileUpload(width=247,
                               height=110,
                               text="Drop keystore file here or",
                               browse_text="browse…")
        self.add(self.file, 5)
        password = Input.Builder().placeholder('Password')\
                                  .name('pwd')\
                                  .mode(Input.Password)\
                                  .model(self.password)\
                                  .build()

        self.add(password, 20)
        self.import_ = Button.Builder().text('Import')\
            .style('primary')\
            .click(lambda _: self._import())\
            .build()
        self.add(self.import_, 5)
        self.loading = Loading()
        self.loading.hide()
        self.add(self.loading)

    def style(self):
        return """ """


class LoginWindow(MyWindow):

    def __init__(self, reactor=None, parent=None):
        super().__init__(reactor)
        self.createWnd = CreateWindow(reactor, self)
        self.importWnd = ImportWindow(reactor, self)

    def show(self):
        app.event.emit(app.events.LOGIN_OPEN)
        super().show()

    def ui(self, layout):
        # Logo
        path = abs_path('icons/logo@2x.png')
        pixm = QPixmap(path)
        scale = 1.3
        pixm = pixm.scaled(168 * scale, 214 * scale)
        logo = Builder().name('logo').pixmap(pixm).build()
        logoLayout = QHBoxLayout()
        logoLayout.setAlignment(Qt.AlignCenter)
        logoLayout.addWidget(logo)
        self.add(logoLayout, 70)

        create = Builder(widget=Button).text('Create New Account')\
                                       .name('create')\
                                       .click(lambda _: self.to(self.createWnd)).build()
        _import = Builder(widget=Button).text('Import Account')\
                                        .name('_import')\
                                        .click(lambda _: self.to(self.importWnd)).build()
        self.add(create, 15)
        self.add(_import)

    def style(self):
        return """
            QLabel#logo {
                margin-top: 60px;
            }
        """
