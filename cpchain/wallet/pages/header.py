from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget, QRadioButton,
                             QFileDialog, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QCursor, QFont, QFontDatabase, QPalette, QBrush, QPixmap

from cpchain.crypto import ECCipher, RSACipher, Encoder

from cpchain.wallet.pages import load_stylesheet, HorizontalLine, wallet, main_wnd, get_pixm, abs_path
from cpchain.wallet.pages.login import LoginWindow


from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from cpchain.wallet import fs
from cpchain.utils import open_file, sizeof_fmt
from cpchain.proxy.client import pick_proxy

import importlib
import os
import os.path as osp
import string
import logging

from cpchain import config, root_dir
from cpchain.wallet.pages import main_wnd, app

logger = logging.getLogger(__name__)

class Header(QFrame):
    class SearchBar(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.init_ui()

        def init_ui(self):
            self.setObjectName("search_bar")
            self.setFixedSize(300, 25)
            self.setTextMargins(25, 0, 20, 0)

            self.search_btn = search_btn = QPushButton(self)
            search_btn.setObjectName("search_btn")
            search_btn.setFixedSize(18, 18)
            search_btn.setCursor(QCursor(Qt.PointingHandCursor))
            self.search_btn.clicked.connect(self.search_act)
            self.returnPressed.connect(self.search_act)

            def set_layout():
                main_layout = QHBoxLayout()
                main_layout.addWidget(search_btn)
                main_layout.addStretch()
                main_layout.setContentsMargins(5, 0, 0, 0)
                self.setLayout(main_layout)
            set_layout()

        @inlineCallbacks
        def query(self):
            item = yield wallet.market_client.query_product(str(self.text()))
            promo = yield wallet.market_client.query_promotion()
            main_wnd.findChild(QWidget, 'search_tab').update_item(item, promo)

        def search_act(self):
            wallet.app.event.emit(wallet.app.events.SEARCH, self.text())

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # self.content_tabs = parent.content_tabs
        self.init_ui()
        self.brush()
    
    def brush(self):
        palette1 = QPalette()
        path = abs_path('icons/header@x2.png')
        palette1.setBrush(self.backgroundRole(), QBrush(QPixmap(path)))
        self.setPalette(palette1)
        self.setAutoFillBackground(True)

    def init_ui(self):
        def create_logos():
            self.logo_label = logo_label = QLabel(self)
            pixmap = get_pixm('header_logo@2x.png')# 'cpc-logo-single.png')
            pixmap = pixmap.scaled(280, 64)
            logo_label.setPixmap(pixmap)
            # self.word_label = QLabel(self)
            # self.word_label.setText("<b>CPChain</b>")
            # self.word_label.setFont(QFont("Roman times", 25, QFont.Bold))
        create_logos()

        def create_search_bar():
            self.search_bar = search_bar = Header.SearchBar(self)
            search_bar.setPlaceholderText("Search")
        create_search_bar()

        def create_btns():
            self.prev_btn = QPushButton("", self)
            def back(event):
                app.router.back()
            self.prev_btn.setObjectName("prev_btn")
            self.prev_btn.clicked.connect(back)

            self.nex_btn = QPushButton("", self)
            def forward(event):
                app.router.forward()
            self.nex_btn.setObjectName("nex_btn")
            self.nex_btn.clicked.connect(forward)

            # self.download_btn = QPushButton("", self)
            # self.download_btn.setObjectName("download_btn")
            # self.download_btn.clicked.connect(self.handle_download)

            # self.upload_btn = QPushButton("", self)
            # self.upload_btn.setObjectName("upload_btn")
            # self.upload_btn.clicked.connect(self.handle_upload)
            # self.upload_btn.setCursor(QCursor(Qt.PointingHandCursor))

            # self.message_btn = QPushButton("", self)
            # self.message_btn.setObjectName("message_btn")
            # self.message_btn.setCursor(QCursor(Qt.PointingHandCursor))

            self.profile_page_btn = QPushButton("", self)
            self.profile_page_btn.setObjectName("profile_page_btn")
            self.profile_page_btn.setCursor(QCursor(Qt.PointingHandCursor))
            self.profile_page_btn.clicked.connect(self.login)

            # self.profile_btn = QPushButton("", self)
            # self.profile_btn.setObjectName("profile_btn")

            self.minimize_btn = QPushButton("", self)
            self.minimize_btn.setObjectName("minimize_btn")
            self.minimize_btn.setFixedSize(15, 15)
            self.minimize_btn.clicked.connect(self.parent.showMinimized)


            self.maximize_btn = QPushButton("", self)
            self.maximize_btn.setObjectName("maximize_btn")
            self.maximize_btn.setFixedSize(15, 15)
            def toggle_maximization():
                state = Qt.WindowFullScreen | Qt.WindowMaximized
                if state & self.parent.windowState():
                    self.parent.showNormal()
                else:
                    self.parent.showMaximized()
            self.maximize_btn.clicked.connect(toggle_maximization)

            self.close_btn = QPushButton("", self)
            self.close_btn.setObjectName("close_btn")
            self.close_btn.setFixedSize(15, 15)
            self.close_btn.clicked.connect(self.parent.close)
        create_btns()

        def set_layout():
            self.all_layout = all_layout = QVBoxLayout(self)
            all_layout.addSpacing(0)

            self.extra_layout = extra_layout = QHBoxLayout(self)
            self.extra_layout.setObjectName('qh_1')
            extra_layout.setContentsMargins(0, 0, 0, 0)
            extra_layout.setAlignment(Qt.AlignRight)
            extra_layout.addWidget(self.minimize_btn)
            extra_layout.addSpacing(2)
            extra_layout.addWidget(self.maximize_btn)
            extra_layout.addSpacing(2)
            extra_layout.addWidget(self.close_btn)
            extra_layout.addSpacing(2)

            self.main_layout = main_layout = QHBoxLayout(self)
            main_layout.setSpacing(0)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addWidget(self.logo_label)
            main_layout.addSpacing(5)
            # main_layout.addWidget(self.word_label)
            main_layout.addSpacing(30)
            main_layout.addWidget(self.prev_btn)
            main_layout.addSpacing(0)
            main_layout.addWidget(self.nex_btn)
            main_layout.addSpacing(28)
            main_layout.addWidget(self.search_bar)
            main_layout.addStretch(20)
            # main_layout.addWidget(self.upload_btn)
            main_layout.addSpacing(18)
            # main_layout.addWidget(self.message_btn)
            main_layout.addSpacing(18)
            # main_layout.addWidget(self.download_btn)
            main_layout.addSpacing(20)
            main_layout.addWidget(self.profile_page_btn)
            main_layout.addSpacing(8)
            # main_layout.addWidget(self.profile_btn)

            all_layout.addLayout(self.extra_layout)
            all_layout.addLayout(self.main_layout)

            self.main_layout.setObjectName('Header')

            self.setLayout(self.all_layout)

        set_layout()

        load_stylesheet(self, "headertest.qss")

    def login(self):
        wnd = LoginWindow()
        wnd.show()

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.m_DragPosition = event.globalPos() - self.parent.pos()
            self.parent.m_drag = True
            event.accept()


    def mouseMoveEvent(self, event):
        try:
            if Qt.LeftButton and event.buttons():
                self.parent.move(event.globalPos()-self.parent.m_DragPosition)
                event.accept()

        except AttributeError:
            pass

    def mouseReleaseEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.m_drag = False
