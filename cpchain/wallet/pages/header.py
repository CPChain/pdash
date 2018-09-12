from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget, QRadioButton,
                             QFileDialog, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QCursor, QFont, QFontDatabase

from cpchain.crypto import ECCipher, RSACipher, Encoder

from cpchain.wallet.pages import load_stylesheet, HorizontalLine, wallet, main_wnd, get_pixm

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
from cpchain.wallet.pages.personal import Seller

from cpchain.wallet.pages.product import Product2, TableWidget

from cpchain.wallet.pages import main_wnd

logger = logging.getLogger(__name__)

class SearchProductTab(QScrollArea):
    def __init__(self, parent=None, key_words=""):
        super().__init__(parent)
        self.parent = parent
        self.key_words = key_words
        self.setObjectName("search_tab")
        self.item_lists = []
        self.promo_lists = []
        self.search_item_num = 4
        self.search_promo_num = 4
        self.init_ui()


    def init_ui(self):

        self.frame = QFrame()
        self.frame.setObjectName("promote_frame")
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(200)
        self.frame.setMaximumWidth(200)

        self.res_label = QLabel("results")
        self.res_label.setObjectName("res_label")

        self.time_label = QLabel("Time")
        self.time_label.setObjectName("time_label")

        self.sales_label = QLabel("Sales")
        self.sales_label.setObjectName("sales_label")

        self.price_label = QLabel("Price")
        self.price_label.setObjectName("price_label")

        self.region_label = QLabel("Region")
        self.region_label.setObjectName("region_label")

        self.line_label = QLabel("-")
        self.line_label.setObjectName("line_label")

        self.may_like_label = QLabel("You may like")
        self.may_like_label.setObjectName("may_like_label")

        self.time_btn = QPushButton(self)
        self.time_btn.setObjectName("time_btn")

        self.sales_btn = QPushButton(self)
        self.sales_btn.setObjectName("sales_btn")

        self.price_btn = QPushButton(self)
        self.price_btn.setObjectName("price_btn")

        self.region_btn = QPushButton(self)
        self.region_btn.setObjectName("region_btn")

        self.region_menu = region_menu = QMenu('Region', self)
        self.shanghai_act = QAction('China', self)
        self.london_act = QAction('London', self)
        self.paris_act = QAction('Paris', self)
        self.more_act = QAction('More', self)

        region_menu.addAction(self.shanghai_act)
        region_menu.addAction(self.london_act)
        region_menu.addAction(self.paris_act)
        region_menu.addAction(self.more_act)

        self.region_btn.setMenu(self.region_menu)


        self.price_edit_from = QLineEdit()
        self.price_edit_from.setObjectName("price_edit_from")

        self.price_edit_to = QLineEdit()
        self.price_edit_to.setObjectName("price_edit_to")


        self.hline = HorizontalLine(self, 2)
        self.num_label = QLabel()

        self.main_layout = QHBoxLayout(self)
        self.stat_layout = QHBoxLayout()
        self.product_layout = QVBoxLayout(self)
        self.promotion_layout = QVBoxLayout(self)
        self.sort_layout = QHBoxLayout(self)

        @inlineCallbacks
        def display_lists():
            self.item_lists = yield wallet.market_client.query_product(self.key_words)
            self.num_label.setText("{}".format(len(self.item_lists)))
            self.num_label.setObjectName("num_label")
            for i in range(len(self.item_lists)):
                self.item_lists[i]['msg_hash'] = self.item_lists[i]['market_hash']
            self.promo_lists = yield wallet.market_client.query_promotion()
            set_layout()

        display_lists()

        def set_layout():
            main_layout = self.main_layout
            main_layout.addSpacing(0)
            main_layout.setContentsMargins(10, 20, 10, 10)

            # self.stat_layout = QHBoxLayout()
            self.stat_layout.addSpacing(0)
            self.stat_layout.addWidget(self.num_label)
            self.stat_layout.addSpacing(0)
            self.stat_layout.addWidget(self.res_label)
            self.stat_layout.addStretch(1)

            # self.product_layout = QVBoxLayout(self)
            self.product_layout.addSpacing(0)

            # self.promotion_layout = QVBoxLayout(self)
            self.promotion_layout.addSpacing(0)

            # self.sort_layout = QHBoxLayout(self)
            self.sort_layout.addSpacing(0)
            self.sort_layout.addWidget(self.time_label)
            self.sort_layout.addSpacing(0)
            self.sort_layout.addWidget(self.time_btn)
            self.sort_layout.addSpacing(0)
            self.sort_layout.addWidget(self.sales_label)
            self.sort_layout.addSpacing(0)
            self.sort_layout.addWidget(self.sales_btn)
            self.sort_layout.addSpacing(0)
            self.sort_layout.addWidget(self.price_label)
            self.sort_layout.addSpacing(0)
            self.sort_layout.addWidget(self.price_btn)
            self.sort_layout.addSpacing(0)
            self.sort_layout.addWidget(self.price_edit_from)
            self.sort_layout.addSpacing(0)
            self.sort_layout.addWidget(self.line_label)
            self.sort_layout.addSpacing(0)
            self.sort_layout.addWidget(self.price_edit_to)
            self.sort_layout.addSpacing(0)
            self.sort_layout.addWidget(self.region_label)
            self.sort_layout.addSpacing(0)
            self.sort_layout.addWidget(self.region_btn)
            self.sort_layout.addStretch(1)

            self.product_layout.addLayout(self.stat_layout)
            self.product_layout.addSpacing(0)
            self.product_layout.addLayout(self.sort_layout)
            self.product_layout.addSpacing(0)

            self.promotion_layout.addWidget(self.may_like_label)
            self.promotion_layout.addSpacing(0)
            self.promotion_layout.addWidget(self.hline)
            self.promotion_layout.addSpacing(0)

            for i in range(self.search_item_num):
                if i > len(self.item_lists) - 1:
                    break
                self.product_layout.addWidget(Product2(self, self.item_lists[i]))
                self.product_layout.addSpacing(0)

            self.product_layout.addStretch(1)

            for i in range(self.search_promo_num):
                if i == len(self.item_lists) - 1:
                    break
                self.promotion_layout.addWidget(Product2(self, self.promo_lists[i], 'simple'))
                self.promotion_layout.addSpacing(0)

            self.promotion_layout.addStretch(1)

            self.main_layout.addLayout(self.product_layout, 2)
            self.main_layout.addLayout(self.promotion_layout, 1)

            self.setLayout(self.main_layout)

            load_stylesheet(self, "searchproduct.qss")

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
            content_tabs = main_wnd.content_tabs
            content_tabs.addTab(SearchProductTab(content_tabs, str(self.text())), "")
            wid = content_tabs.findChild(QWidget, "search_tab")
            content_tabs.setCurrentWidget(wid)


    class LoginDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.setWindowTitle("Log in")

            self.init_ui()

        def init_ui(self):
            def create_btns():
                self.account1_btn = account1_btn = QRadioButton(self)
                account1_btn.setText("Account 1")
                account1_btn.setObjectName("account1_btn")
                account1_btn.setChecked(True)
                self.account2_btn = account2_btn = QRadioButton(self)
                account2_btn.setText("Account 2")
                account2_btn.setObjectName("account2_btn")

                self.cancel_btn = cancel_btn = QPushButton("Cancel")
                cancel_btn.setObjectName("cancel_btn")
                self.login_btn = login_btn = QPushButton("Log in")
                login_btn.setObjectName("login_btn")
            create_btns()

            def create_labels():
                self.choice_label = choice_label = QLabel("Please select which account you would like to log in: ")
                choice_label.setObjectName("choice_label")
            create_labels()

            def bind_slots():
                self.cancel_btn.clicked.connect(self.handle_cancel)
                self.login_btn.clicked.connect(self.handle_login)
            bind_slots()

            def set_layout():
                self.main_layout = main_layout = QVBoxLayout()
                main_layout.addSpacing(0)
                main_layout.addWidget(self.choice_label)
                main_layout.addSpacing(2)
                main_layout.addWidget(self.account1_btn)
                main_layout.addSpacing(1)
                main_layout.addWidget(self.account2_btn)
                self.confirm_layout = confirm_layout = QHBoxLayout()
                confirm_layout.addSpacing(0)
                confirm_layout.addWidget(self.cancel_btn)
                confirm_layout.addSpacing(2)
                confirm_layout.addWidget(self.login_btn)

                main_layout.addLayout(self.confirm_layout)
                self.setLayout(self.main_layout)
            set_layout()

            self.show()

        def handle_cancel(self):
            self.account1_btn.setChecked(True)
            self.account2_btn.setChecked(False)

            self.close()

        def handle_login(self):
            if self.account2_btn.isChecked():
                wallet.accounts.set_default_account(1)
                wallet.market_client.account = wallet.accounts.default_account
                wallet.market_client.public_key = ECCipher.serialize_public_key(wallet.market_client.account.public_key)

            d_login = wallet.market_client.login()
            def login_result(status):
                if status == 1:
                    QMessageBox.information(main_wnd, 'Tips', 'Log in successfully!')
                elif status == 0:
                    QMessageBox.information(main_wnd, 'Tips', 'Failed to log in !')
                else:
                    QMessageBox.information(main_wnd, 'Tips', 'New users !')
            d_login.addCallback(login_result)
            self.close()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.content_tabs = parent.content_tabs
        self.init_ui()

    def init_ui(self):
        def create_logos():
            self.logo_label = logo_label = QLabel(self)
            pixmap = get_pixm('cpc-logo-single.png')
            pixmap = pixmap.scaled(45, 45)
            logo_label.setPixmap(pixmap)
            self.word_label = QLabel(self)
            self.word_label.setText("<b>CPChain</b>")
            self.word_label.setFont(QFont("Roman times", 25, QFont.Bold))
        create_logos()

        def create_search_bar():
            self.search_bar = search_bar = Header.SearchBar(self)
            search_bar.setPlaceholderText("Search")
        create_search_bar()

        def create_btns():
            self.prev_btn = QPushButton("", self)
            self.prev_btn.setObjectName("prev_btn")

            self.nex_btn = QPushButton("", self)
            self.nex_btn.setObjectName("nex_btn")

            self.download_btn = QPushButton("", self)
            self.download_btn.setObjectName("download_btn")
            self.download_btn.clicked.connect(self.handle_download)

            self.upload_btn = QPushButton("", self)
            self.upload_btn.setObjectName("upload_btn")
            self.upload_btn.clicked.connect(self.handle_upload)
            self.upload_btn.setCursor(QCursor(Qt.PointingHandCursor))

            self.message_btn = QPushButton("", self)
            self.message_btn.setObjectName("message_btn")
            self.message_btn.setCursor(QCursor(Qt.PointingHandCursor))

            self.profile_page_btn = QPushButton("", self)
            self.profile_page_btn.setObjectName("profile_page_btn")
            self.profile_page_btn.setCursor(QCursor(Qt.PointingHandCursor))
            self.profile_page_btn.clicked.connect(self.login)

            self.profile_btn = QPushButton("", self)
            self.profile_btn.setObjectName("profile_btn")

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

            def create_popmenu():
                self.profile_menu = profile_menu = QMenu('Profile', self)
                profile_view_act = QAction('Profile Settings', self)
                profile_view_act.triggered.connect(self.profile_view_act_triggered)
                preference_act = QAction('Preference', self)
                preference_act.triggered.connect(self.preference_act_triggered)
                security_act = QAction('Accout Security', self)
                security_act.triggered.connect(self.security_act_triggered)

                profile_menu.addAction(profile_view_act)
                profile_menu.addAction(preference_act)
                profile_menu.addAction(security_act)
            create_popmenu()
            self.profile_btn.setMenu(self.profile_menu)

        create_btns()


        def set_layout():
            self.all_layout = all_layout = QVBoxLayout(self)
            all_layout.addSpacing(0)

            self.extra_layout = extra_layout = QHBoxLayout(self)
            extra_layout.addStretch(1)
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
            main_layout.addWidget(self.word_label)
            main_layout.addSpacing(30)
            main_layout.addWidget(self.prev_btn)
            main_layout.addSpacing(0)
            main_layout.addWidget(self.nex_btn)
            main_layout.addSpacing(28)
            main_layout.addWidget(self.search_bar)
            main_layout.addStretch(20)
            main_layout.addWidget(self.upload_btn)
            main_layout.addSpacing(18)
            main_layout.addWidget(self.message_btn)
            main_layout.addSpacing(18)
            main_layout.addWidget(self.download_btn)
            main_layout.addSpacing(20)
            main_layout.addWidget(self.profile_page_btn)
            main_layout.addSpacing(8)
            main_layout.addWidget(self.profile_btn)

            all_layout.addLayout(self.extra_layout)
            all_layout.addLayout(self.main_layout)

            self.setLayout(self.all_layout)

        set_layout()

        load_stylesheet(self, "headertest.qss")

    def login(self):
        self.login_dialog = Header.LoginDialog(self)

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

    def profile_view_act_triggered(self):
        wid = self.content_tabs.findChild(QWidget, "personalprofile_tab")
        self.content_tabs.setCurrentWidget(wid)
        self.parent.findChild(QWidget, 'personalprofile_tab').set_one_index()

    def preference_act_triggered(self):
        wid = self.content_tabs.findChild(QWidget, "personalprofile_tab")
        self.content_tabs.setCurrentWidget(wid)
        self.parent.findChild(QWidget, 'personalprofile_tab').set_two_index()

    def security_act_triggered(self):
        wid = self.content_tabs.findChild(QWidget, "personalprofile_tab")
        self.content_tabs.setCurrentWidget(wid)
        self.parent.findChild(QWidget, 'personalprofile_tab').set_three_index()

    def handle_download(self):
        wid = self.content_tabs.findChild(QWidget, "purchase_tab")
        wid.purchased_main_tab.setCurrentIndex(1)
        self.content_tabs.setCurrentWidget(wid)

    def handle_upload(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self.parent, "Tips", "Please login first !")
            return
        wid = self.parent.content_tabs.findChild(QWidget, "cloud_tab")
        self.upload_dlg = CloudTab.UploadDialog(wid)
        self.upload_dlg.show()


class CloudTab(QScrollArea):
    class SearchBar(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.init_ui()

        def init_ui(self):
            self.setObjectName("search_bar")
            self.setTextMargins(25, 0, 20, 0)

            self.search_btn_cloud = search_btn_cloud = QPushButton(self)
            search_btn_cloud.setObjectName("search_btn_cloud")
            search_btn_cloud.setFixedSize(18, 18)
            search_btn_cloud.setCursor(QCursor(Qt.PointingHandCursor))


            def set_layout():
                main_layout = QHBoxLayout()
                main_layout.addWidget(search_btn_cloud)
                main_layout.addStretch()
                main_layout.setContentsMargins(5, 0, 0, 0)
                self.setLayout(main_layout)
            set_layout()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("cloud_tab")

        self.init_ui()

    def update_table(self):
        tab_index = main_wnd.main_tab_index["cloud_tab"]
        main_wnd.content_tabs.removeTab(tab_index)
        tab_index = main_wnd.content_tabs.addTab(CloudTab(main_wnd.content_tabs), "")
        main_wnd.main_tab_index["cloud_tab"] = tab_index
        main_wnd.content_tabs.setCurrentIndex(tab_index)

    def set_right_menu(self, func):
        self.customContextMenuRequested[QPoint].connect(func)


    def init_ui(self):

        self.check_list = []
        self.num_file = 100
        self.cur_clicked = 0
        self.total_label = total_label = QLabel("{} Files".format(self.num_file))
        total_label.setObjectName("total_label")

        self.delete_btn = delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("delete_btn")
        self.delete_btn.clicked.connect(self.handle_delete)
        self.upload_btn = upload_btn = QPushButton("Upload")
        upload_btn.setObjectName("upload_btn")

        self.upload_btn.clicked.connect(self.handle_upload)

        self.search_bar = CloudTab.SearchBar(self)

        self.time_rank_label = time_rank_label = QLabel("Time")
        time_rank_label.setObjectName("time_rank_label")

        self.tag_rank_label = tag_rank_label = QLabel("Tag")
        tag_rank_label.setObjectName("tag_rank_label")
        def create_file_table():
            self.file_table = file_table = TableWidget(self)
            def right_menu():
                self.cloud_right_menu = QMenu(self.file_table)
                self.cloud_delete_act = QAction('Delete', self)
                self.cloud_publish_act = QAction('Publish', self)

                self.cloud_delete_act.triggered.connect(self.handle_delete_act)
                self.cloud_publish_act.triggered.connect(self.handle_publish_act)

                self.cloud_right_menu.addAction(self.cloud_delete_act)
                self.cloud_right_menu.addAction(self.cloud_publish_act)

                self.cloud_right_menu.exec_(QCursor.pos())

            self.file_table.horizontalHeader().setStretchLastSection(True)
            self.file_table.verticalHeader().setVisible(False)
            self.file_table.setShowGrid(False)
            self.file_table.setAlternatingRowColors(True)
            self.file_table.resizeColumnsToContents()
            self.file_table.resizeRowsToContents()
            self.file_table.setFocusPolicy(Qt.NoFocus)

            file_table.horizontalHeader().setHighlightSections(False)
            file_table.setColumnCount(6)
            file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            file_table.set_right_menu(right_menu)
            file_table.setHorizontalHeaderLabels(['', 'Product Name', 'Size', 'Remote Type', 'Published', 'ID'])
            file_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            file_table.horizontalHeader().setFixedHeight(35)
            file_table.verticalHeader().setDefaultSectionSize(30)
            file_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
            file_table.setSortingEnabled(True)

            self.file_list = fs.get_file_list()

            self.check_record_list = []
            self.checkbox_list = []
            self.row_number = len(self.file_list)
            self.file_table.setRowCount(self.row_number)

            for cur_row in range(self.row_number):
                logger.debug('current file id: %s', self.file_list[cur_row].id)
                logger.debug('current file name: %s', self.file_list[cur_row].name)
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                self.file_table.setItem(cur_row, 0, checkbox_item)
                self.file_table.setItem(cur_row, 1, QTableWidgetItem(self.file_list[cur_row].name))
                self.file_table.setItem(cur_row, 2, QTableWidgetItem(sizeof_fmt(self.file_list[cur_row].size)))
                self.file_table.setItem(cur_row, 3, QTableWidgetItem(self.file_list[cur_row].remote_type))
                self.file_table.setItem(cur_row, 4, QTableWidgetItem(str(self.file_list[cur_row].is_published)))
                self.file_table.setItem(cur_row, 5, QTableWidgetItem(str(self.file_list[cur_row].id)))
                self.check_record_list.append(False)
        create_file_table()
        self.file_table.sortItems(2)
        self.file_table.horizontalHeader().setStyleSheet("QHeaderView::section{background: #f3f3f3; border: 1px solid #dcdcdc}")
        def record_check(item):
            self.cur_clicked = item.row()
            if item.checkState() == Qt.Checked:
                self.check_record_list[item.row()] = True
        self.file_table.itemClicked.connect(record_check)

        def set_layout():
            self.main_layout = main_layout = QVBoxLayout(self)
            main_layout.addSpacing(0)
            self.layout1 = QHBoxLayout(self)
            self.layout1.addWidget(self.search_bar)
            self.layout1.addSpacing(10)
            self.layout1.addWidget(self.time_rank_label)
            self.layout1.addSpacing(10)
            self.layout1.addWidget(self.tag_rank_label)
            self.layout1.addStretch(1)
            self.layout1.addWidget(self.delete_btn)
            self.layout1.addSpacing(5)
            self.layout1.addWidget(self.upload_btn)
            self.layout1.addSpacing(5)

            self.main_layout.addLayout(self.layout1)
            self.main_layout.addSpacing(2)
            self.main_layout.addWidget(self.file_table)
            self.setLayout(self.main_layout)
        set_layout()
        load_stylesheet(self, "cloud.qss")

    def handle_delete(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
            return
        for i in range(len(self.check_record_list)):
            logger.debug(self.check_record_list)
            if self.check_record_list[i] is True:
                file_id = self.file_table.item(i, 5).text()
                fs.delete_file_by_id(file_id)
                self.file_table.removeRow(i)
                d_status = wallet.market_client.delete_file_info(file_id)
                def update_market_backup(status):
                    if status == 1:
                        QMessageBox.information(self, "Tips", "Deleted from market backup successfully!")
                    else:
                        QMessageBox.information(self, "Tips", "Failed to delete record from market backup!")
                d_status.addCallback(update_market_backup)
        self.check_record_list = [False for i in range(self.file_table.rowCount())]

    class UploadDialog(QDialog):
        def __init__(self, storage_type=None):
            super().__init__()
            self.resize(500, 180)
            self.setWindowTitle("Upload your file")
            self.storage_type = storage_type
            self.dst = dict()
            self.label_list = []
            self.edit_list = []
            self.init_ui()

        def init_ui(self):

            def create_btns():
                self.cancel_btn = QPushButton("Cancel")
                self.cancel_btn.setObjectName("cancel_btn")
                self.ok_btn = QPushButton("OK")
                self.ok_btn.setObjectName("ok_btn")
                self.file_choose_btn = QPushButton("Open File")
                self.file_choose_btn.setObjectName("file_choose_btn")
            create_btns()

            def bind_slots():
                self.cancel_btn.clicked.connect(self.handle_cancel)
                self.ok_btn.clicked.connect(self.handle_ok)
                self.file_choose_btn.clicked.connect(self.handle_choose_file)
            bind_slots()

            storage_module = importlib.import_module(
                "cpchain.storage-plugin." + self.storage_type
            )
            storage = storage_module.Storage()
            self.dst_default = storage.user_input_param()
            self.dst = self.dst_default

            def create_labels():
                for key in self.dst:
                    parameter_label = QLabel(key)
                    parameter_label.setObjectName("parameter_label" + key)
                    parameter_label.setWordWrap(True)
                    self.label_list.append(parameter_label)
            create_labels()

            def create_edits():
                for key in self.dst:
                    parameter_edit = QLineEdit()
                    parameter_edit.setObjectName("parameter_edit" + key)
                    parameter_edit.setText(str(self.dst[key]))
                    self.edit_list.append(parameter_edit)
            create_edits()

            def set_layout():
                self.main_layout = main_layout = QVBoxLayout(self)
                main_layout.addSpacing(0)
                for i in range(len(self.dst)):
                    hlayout = QHBoxLayout(self)
                    hlayout.addWidget(self.label_list[i])
                    hlayout.addSpacing(2)
                    hlayout.addWidget(self.edit_list[i])
                    main_layout.addLayout(hlayout)
                    main_layout.addSpacing(2)

                main_layout.addWidget(self.file_choose_btn)
                main_layout.addSpacing(2)

                self.confirm_layout = confirm_layout = QHBoxLayout()
                confirm_layout.addStretch(1)
                confirm_layout.addWidget(self.ok_btn)
                confirm_layout.addSpacing(20)
                confirm_layout.addWidget(self.cancel_btn)
                confirm_layout.addStretch(1)

                main_layout.addSpacing(10)
                main_layout.addLayout(self.confirm_layout)
                main_layout.addSpacing(5)
                self.setLayout(self.main_layout)
            set_layout()
            load_stylesheet(self, "uploaddialog.qss")

        def handle_choose_file(self):
            self.file_choice = QFileDialog.getOpenFileName()[0]

        def handle_cancel(self):
            self.file_choice = ""
            self.close()

        def handle_ok(self):
            flag = True
            index = 0
            for key in self.dst:
                arg = self.edit_list[index].text()
                if not arg:
                    flag = False
                    break
                self.dst[key] = arg
                index += 1

            if flag is False:
                QMessageBox.warning(self, "Warning", "Please input all the required fields first")
                return

            if self.file_choice == "":
                QMessageBox.warning(self, "Warning", "Please select your files to upload first !")
                return
            d_upload = deferToThread(fs.upload_file, self.file_choice, self.storage_type, self.dst)
            d_upload.addCallback(self.handle_ok_callback)

            self.close()

        def handle_ok_callback(self, file_id):
            file_info = fs.get_file_by_id(file_id)
            hashcode = file_info.hashcode
            path = file_info.path
            size = file_info.size
            product_id = file_info.id
            remote_type = file_info.remote_type
            remote_uri = file_info.remote_uri
            name = file_info.name
            logger.debug('encrypt aes key')
            encrypted_key = RSACipher.encrypt(file_info.aes_key)
            encrypted_key = Encoder.bytes_to_base64_str(encrypted_key)
            d = wallet.market_client.upload_file_info(hashcode, path, size, product_id, remote_type, remote_uri, name, encrypted_key)
            def handle_upload_resp(status):
                if status == 1:
                    tab_index = main_wnd.main_tab_index['cloud_tab']
                    for key in main_wnd.main_tab_index:
                        if main_wnd.main_tab_index[key] > tab_index:
                            main_wnd.main_tab_index[key] -= 1
                    main_wnd.content_tabs.removeTab(tab_index)
                    tab_index = main_wnd.content_tabs.addTab(CloudTab(main_wnd.content_tabs), "")
                    main_wnd.main_tab_index['cloud_tab'] = tab_index
                    main_wnd.content_tabs.setCurrentIndex(tab_index)

                    logger.debug("update table successfully!")
                    QMessageBox.information(self, "Tips", "Uploaded successfuly")
                else:
                    logger.debug('upload file info to market failed')
            d.addCallback(handle_upload_resp)

    class StorageSelectionDlg(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.resize(300, 400)
            self.setObjectName("storage_selection_dlg")
            self.setWindowTitle("Select your storage service")
            self.service_list = []
            self.list_widget = QListWidget()
            self.init_ui()

        def init_ui(self):
            self.list_widget.setObjectName("storage_service_list")
            path = osp.join(root_dir, "cpchain/storage-plugin")
            self.service_list = [osp.splitext(name)[0] for name in os.listdir(path) if name != 'template.py' and name != '__init__.py' and name != '__pycache__']

            for service in self.service_list:
                item = QListWidgetItem(service)
                self.list_widget.addItem(item)
            self.confirm_btn = QPushButton("Confirm")
            self.confirm_btn.setObjectName("confirm_btn")
            self.cancel_btn = QPushButton("Cancel")
            self.cancel_btn.setObjectName("cancel_btn")

            self.confirm_btn.clicked.connect(self.handle_confirm)
            self.cancel_btn.clicked.connect(self.handle_cancel)

            def set_layout():
                self.main_layout = QVBoxLayout()
                self.main_layout.addSpacing(0)

                self.main_layout.addWidget(self.list_widget)
                self.main_layout.addSpacing(0)

                self.btn_layout = QHBoxLayout()
                self.btn_layout.addSpacing(30)
                self.btn_layout.addWidget(self.cancel_btn)
                self.btn_layout.addSpacing(2)
                self.btn_layout.addWidget(self.confirm_btn)

                self.main_layout.addLayout(self.btn_layout)
                self.setLayout(self.main_layout)

            set_layout()
            logger.debug("Loading stylesheets of SelectionDialog")
            load_stylesheet(self, "selectiondialog.qss")
            self.show()

        def handle_confirm(self):
            # fixme: list widget item check
            cur_row = self.list_widget.currentRow()
            storage_service = self.service_list[cur_row]
            self.upload_dlg = CloudTab.UploadDialog(storage_service)
            self.close()
            self.upload_dlg.show()

        def handle_cancel(self):
            self.close()

    def handle_upload(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
            return
        self.storage_dialog = CloudTab.StorageSelectionDlg(self)

    def handle_delete_act(self):
        self.file_table.removeRow(self.cur_clicked)

    def handle_publish_act(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
        else:
            product_id = self.file_table.item(self.cur_clicked, 5).text()
            self.publish_dialog = PublishDialog(self, product_id=product_id, tab='cloud')
