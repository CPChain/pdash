#!/usr/bin/python3

import sys
import os.path as osp
import string
import hashlib
import logging

from PyQt5.QtWidgets import (QMainWindow, QApplication, QFrame, QDesktopWidget, QPushButton, QHBoxLayout, QMessageBox, QVBoxLayout, QGridLayout, QScrollArea, QListWidget, QListWidgetItem, QTabWidget, QLabel, QWidget, QLineEdit, QTableWidget, QTextEdit, QAbstractItemView, QTableWidgetItem, QMenu, QHeaderView, QAction, QFileDialog, QDialog, QRadioButton, QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, QPoint, QBasicTimer
from PyQt5.QtGui import QIcon, QCursor, QPixmap, QFont, QFontDatabase

from cpchain.wallet.wallet import Wallet
from cpchain import config, root_dir
from cpchain.wallet import fs
from cpchain.crypto import ECCipher, RSACipher, Encoder
from cpchain.utils import open_file, sizeof_fmt
from cpchain.proxy.node import pick_proxy

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from twisted.internet.task import LoopingCall
from twisted.logger import globalLogBeginner, textFileLogObserver

globalLogBeginner.beginLoggingTo([textFileLogObserver(sys.stdout)])
wallet = Wallet(reactor)
logger = logging.getLogger(__name__)

def get_icon(name):
    path = osp.join(root_dir, "cpchain/assets/wallet/icons", name)
    return QIcon(path)

def get_pixm(name):
    path = osp.join(root_dir, "cpchain/assets/wallet/icons", name)
    return QPixmap(path)



def load_stylesheet(wid, name):
    path = osp.join(root_dir, "cpchain/assets/wallet/qss", name)

    subs = dict(asset_dir=osp.join(root_dir, "cpchain/assets/wallet"))

    with open(path) as f:
        s = string.Template(f.read())
        wid.setStyleSheet(s.substitute(subs))

# widgets

class PersonalProfileTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("personalprofile_tab")
        self.init_ui()

    def init_ui(self):

        self.profile_tabs = profile_tabs = QTabWidget(self)
        profile_tabs.setObjectName("profile_tabs")
        profile_tabs.addTab(PersonalInfoPage(profile_tabs), "Personal Information")
        profile_tabs.addTab(PreferenceTab(profile_tabs), "Preference")
        profile_tabs.addTab(SecurityTab(profile_tabs), "Account Security")

        def set_layout():
            follow_main_layout = QHBoxLayout()
            follow_main_layout.addWidget(self.profile_tabs)
            self.setLayout(follow_main_layout)
        set_layout()
        load_stylesheet(self, "personalprofile.qss")

    def set_one_index(self):
        self.profile_tabs.setCurrentIndex(0)

    def set_two_index(self):
        self.profile_tabs.setCurrentIndex(1)

    def set_three_index(self):
        self.profile_tabs.setCurrentIndex(2)


class TagHPTab(QScrollArea):
    def __init__(self, parent=None, key_words=""):
        super().__init__(parent)
        self.parent = parent
        self.key_words = key_words
        self.setObjectName("tagHP_tab")
        self.tag = ""
        self.init_ui()

    def init_ui(self):

        self.search_item_num = 4
        self.search_promo_num = 4

        self.item_lists = []
        self.promo_lists = []

        def get_products(item=None):
            for i in range(self.search_item_num):
                self.item_lists.append(Product(self, item))

        self.item = {"title": "Medical data from NHIS", "none": "none"}
        get_products(self.item)

        def get_promotion(item=None):
            for i in range(self.search_promo_num):
                self.promo_lists.append(Product(self, item, "simple"))
        get_promotion(self.item)

        self.tag_header = QLabel("Tag 1")
        self.tag_header.setObjectName("tag_header")

        self.followthis_label = QPushButton("Follow this tag")
        self.followthis_label.setObjectName("followthis_label")
        self.followthis_label.clicked.connect(self.handle_follow_tag)

        self.related_label = QLabel("Related Tags")
        self.related_label.setObjectName("related_label")

        self.may_like_label = QLabel("You may like")
        self.may_like_label.setObjectName("may_like_label")

        def bind_slots():
            logger.debug("binding slots of btns....")

        bind_slots()

        self.hline_1 = HorizontalLine(self, 2)
        self.hline_2 = HorizontalLine(self, 2)
        self.hline_3 = HorizontalLine(self, 2)
        self.main_layout = main_layout = QHBoxLayout(self)
        main_layout.addSpacing(0)

        self.content_layout = QVBoxLayout(self)
        self.stat_layout = QHBoxLayout()
        self.stat_layout.addSpacing(0)
        self.stat_layout.addWidget(self.tag_header)
        self.stat_layout.addStretch(1)
        self.stat_layout.addWidget(self.followthis_label)
        self.stat_layout.addSpacing(0)

        self.content_layout.addLayout(self.stat_layout)
        self.content_layout.addWidget(self.hline_1)
        for i in range(self.search_item_num):
            self.content_layout.addWidget(self.item_lists[i])
            self.content_layout.addSpacing(0)

        self.content_layout.addStretch(1)

        self.promotion_layout = QVBoxLayout(self)
        self.promotion_layout.addWidget(self.related_label)
        self.promotion_layout.addWidget(self.hline_2)
        self.promotion_layout.addWidget(self.may_like_label)
        self.promotion_layout.addWidget(self.hline_3)

        for i in range(self.search_promo_num):
            self.promotion_layout.addWidget(self.promo_lists[i])
            self.promotion_layout.addSpacing(0)

        self.main_layout.addLayout(self.content_layout, 2)
        self.main_layout.addLayout(self.promotion_layout, 1)

        self.main_layout.addLayout(self.content_layout)

        self.setLayout(self.main_layout)

        logger.debug("loading stylesheet...")
        load_stylesheet(self, "tagpage.qss")

    def handle_follow_tag(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
            return
        self.tag = 'tag1'
        d_status = wallet.market_client.add_follow_tag(self.tag)
        def handle_state(status):
            if status == 1:
                QMessageBox.information(self, "Tips", "Successfully followed this tag")
            else:
                QMessageBox.information(self, "Tips", "Problem occurred when following seller")
        d_status.addCallback(handle_state)


class SellerHPTab(QScrollArea):
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

            def set_layout():
                main_layout = QHBoxLayout()
                main_layout.addWidget(search_btn)
                main_layout.addStretch()
                main_layout.setContentsMargins(5, 0, 0, 0)
                self.setLayout(main_layout)

            set_layout()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.seller_addr = "2af2e6a7da5c788f6a73abf67bb8acb809d7ff54"
        self.setObjectName("sellerHP_tab")
        self.init_ui()

    def init_ui(self):

        self.time_label = QLabel("Time")
        self.time_label.setObjectName("time_label")

        self.price_label = QLabel("Price")
        self.price_label.setObjectName("price_label")


        self.time_btn = QPushButton(self)
        self.time_btn.setObjectName("time_btn")

        self.price_btn = QPushButton(self)
        self.price_btn.setObjectName("price_btn")

        self.message_btn = QPushButton(self)
        self.message_btn.setObjectName("message_btn")
        self.message_btn.setText("Message")

        self.follow_btn = QPushButton(self)
        self.follow_btn.setObjectName("follow_btn")
        self.follow_btn.setText("Follow")
        self.follow_btn.clicked.connect(self.handle_follow)

        self.seller_list = []
        self.seller_promote_number = 3
        self.item_lists = []
        self.item_num = 4
        self.search_bar = SellerHPTab.SearchBar(self)
        self.this_seller = Seller(self)

        for i in range(self.seller_promote_number):
            self.seller_list.append(Seller(self))

        self.sellerid = {"name": "Chak", "sales": "2020"}
        self.item = {"title": "Medical data from NHIS", "none": "none"}

        for i in range(self.item_num):
            self.item_lists.append(Product(self, self.item))

        self.main_layout = main_layout = QHBoxLayout(self)
        main_layout.addSpacing(0)

        self.content_layout = QVBoxLayout(self)
        self.search_layout = QHBoxLayout(self)
        self.search_layout.addWidget(self.search_bar)
        self.search_layout.addSpacing(10)
        self.search_layout.addWidget(self.time_label)
        self.search_layout.addSpacing(0)
        self.search_layout.addWidget(self.time_btn)
        self.search_layout.addSpacing(0)
        self.search_layout.addWidget(self.price_label)
        self.search_layout.addSpacing(0)
        self.search_layout.addWidget(self.price_btn)

        self.content_layout.addLayout(self.search_layout)

        for i in range(self.item_num):
            self.content_layout.addWidget(self.item_lists[i])
            self.content_layout.addSpacing(0)

        self.seller_layout = QVBoxLayout(self)
        self.seller_layout.addWidget(self.this_seller)
        self.btn_layout = QHBoxLayout(self)
        self.btn_layout.addWidget(self.message_btn)
        self.btn_layout.addWidget(self.follow_btn)
        self.seller_layout.addLayout(self.btn_layout)
        self.seller_layout.addSpacing(15)

        for i in range(self.seller_promote_number):
            self.seller_layout.addWidget(self.seller_list[i])
            self.seller_layout.addSpacing(0)

        self.main_layout.addLayout(self.content_layout, 2)
        self.main_layout.addLayout(self.seller_layout, 1)
        self.setLayout(self.main_layout)
        load_stylesheet(self, "sellerhomepage.qss")

    def handle_follow(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
            return
        seller_publick_key = '040ceb41bf5f9a96c16b1441f5edc0277bfa2d0ce6a10b481b14de96b0d03cdc5a43668c6f2fb35ac79f70ba7ea86f036cc37ec814f67e066c4ff65648f829dfe7'
        d_status = wallet.market_client.add_follow_seller(seller_publick_key)
        def handle_state(status):
            if status == 1:
                self.follow_btn.setText("Unfollow")
            else:
                QMessageBox.information(self, "Tips", "Problem occurred when following seller")
        d_status.addCallback(handle_state)


class Seller(QScrollArea):
    def __init__(self, parent=None, sellerid=None, mode=""):
        super().__init__(parent)
        self.parent = parent
        self.sellerid = sellerid
        self.mode = mode
        self.init_ui()

    def init_ui(self):
        self.setMinimumHeight(200)
        self.setMaximumHeight(500)
        self.setMinimumHeight(120)
        self.setMaximumHeight(120)
        self.seller_name = QPushButton("Barack Obama")
        self.seller_name.setObjectName("seller_name")
        self.seller_name.setCursor(QCursor(Qt.PointingHandCursor))

        self.seller_avatar = QLabel(self)
        self.seller_avatar.setObjectName("seller_avatar")

        seller_product_value = 20
        seller_sales_volume = 3455
        self.product_label = QLabel("Products {}".format(seller_product_value))
        self.sales_volume = QLabel("Sales Volume {}".format(seller_sales_volume))

        self.hline = HorizontalLine(self, 2)

        self.main_layout = QGridLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.seller_avatar, 1, 1, 2, 3)
        self.main_layout.addWidget(self.seller_name, 1, 3, 1, 1)
        self.main_layout.addWidget(self.product_label, 2, 3, 1, 1)
        self.main_layout.addWidget(self.sales_volume, 3, 3, 1, 1)
        self.main_layout.addWidget(self.hline, 4, 1, 1, 3)
        self.setLayout(self.main_layout)
        load_stylesheet(self, "selleritem.qss")



class BuyNowDialog(QDialog):
    account_balance = 1500000
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.parent = parent
        self.item = item
        self.resize(300, 180)
        self.setObjectName("buynowdialog")
        self.init_ui()

    def init_ui(self):

        self.needtopay_label = needtopay_label = QLabel("You need to pay:")
        needtopay_label.setObjectName("needtopay_label")
        self.account_label = account_label = QLabel("Account:")
        account_label.setObjectName("account_label")
        self.password_label = password_label = QLabel("Payment password:")
        password_label.setObjectName("password_label")

        self.price_to_pay = self.item['price']
        self.price_value = price_value = QLabel("${}".format(self.price_to_pay))
        price_value.setObjectName("price_value")
        self.account_value = account_value = QLabel("${}".format(BuyNowDialog.account_balance))
        account_value.setObjectName("account_value")

        self.password_input = password_input = QLineEdit()
        password_input.setObjectName("password_input")
        password_input.setEchoMode(QLineEdit.Password)

        self.cancel_btn = QPushButton(self)
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setText("Cancel")
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.clicked.connect(self.handle_cancel)

        self.confirm_btn = QPushButton(self)
        self.confirm_btn.setObjectName("confirm_btn")
        self.confirm_btn.setText("Confirm")
        self.confirm_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.confirm_btn.clicked.connect(self.handle_confirm)

        self.pinfo_top_layout = pinfo_top_layout = QGridLayout(self)
        self.pinfo_top_layout.setContentsMargins(40, 40, 10, 10)
        self.pinfo_top_layout.addWidget(self.needtopay_label, 1, 1, 1, 1)
        self.pinfo_top_layout.addWidget(self.price_value, 1, 3, 1, 1)
        self.pinfo_top_layout.addWidget(self.account_label, 2, 1, 1, 1)
        self.pinfo_top_layout.addWidget(self.account_value, 2, 3, 1, 1)
        self.pinfo_top_layout.addWidget(self.password_label, 3, 1, 1, 1)
        self.pinfo_top_layout.addWidget(self.password_input, 3, 3, 1, 5)

        self.btn_layout = QHBoxLayout(self)
        self.btn_layout.addStretch(1)
        self.btn_layout.addWidget(self.cancel_btn)
        self.btn_layout.addSpacing(10)
        self.btn_layout.addWidget(self.confirm_btn)
        self.btn_layout.addSpacing(5)
        self.pinfo_top_layout.addLayout(self.btn_layout, 5, 1, 3, 5)

        self.setLayout(pinfo_top_layout)
        load_stylesheet(self, "buynowdialog.qss")
        self.show()

    def handle_confirm(self):
        d = pick_proxy()
        def get_proxy_address(proxy_addr):
            msg_hash = self.item['market_hash']
            file_title = self.item['title']
            proxy = proxy_addr
            seller = self.item['owner_address']
            wallet.chain_broker.handler.buy_product(msg_hash, file_title, proxy, seller)
        d.addCallback(get_proxy_address)

        BuyNowDialog.account_balance -= self.price_to_pay
        self.close()

    def handle_cancel(self):
        self.close()


class ProductDetailTab(QScrollArea):
    class ProductComment(QScrollArea):
        def __init__(self, parent=None, comment=None):
            super().__init__()
            self.parent = parent
            self.comment = comment
            self.init_ui()

        def init_ui(self):

            self.path = osp.join(root_dir, "cpchain/assets/wallet/font", "ARLRDBD.TTF")
            self.font_regular = QFontDatabase.addApplicationFont(str(self.path))
            self.font_givenname = QFontDatabase.applicationFontFamilies(self.font_regular)[0]
            self.setFont(QFont(self.font_givenname))

            self.setContentsMargins(0, 0, 0, 0)
            self.setMinimumHeight(120)
            self.setMaximumHeight(120)

            self.avatar_label = QLabel("")
            self.avatar_label.setObjectName("avatar_label")
            pixmap = get_pixm('avatar.jpeg')
            pixmap = pixmap.scaled(40, 40)
            self.avatar_label.setPixmap(pixmap)

            username = self.comment['username']
            if self.comment['username'] == "":
                username = "Dcda Ali"
            self.name_label = QLabel(username)
            self.name_label.setObjectName('name_label')

            self.rating_label = QLabel("{}".format(self.comment['rating']))
            self.rating_label.setObjectName('rating_label')

            self.description_label = QLabel(self.comment['content'])
            self.description_label.setObjectName("description_label")

            self.main_layout = main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addSpacing(0)

            self.basic_layout = QHBoxLayout(self)
            self.basic_layout.setContentsMargins(0, 5, 0, 5)
            self.basic_layout.addSpacing(1)
            self.basic_layout.addWidget(self.avatar_label)
            self.basic_layout.addSpacing(0)
            self.basic_layout.addWidget(self.name_label)
            self.basic_layout.addSpacing(60)
            self.basic_layout.addWidget(self.rating_label)

            self.main_layout.addLayout(self.basic_layout)
            self.main_layout.addSpacing(1)
            self.main_layout.addWidget(self.description_label)

            self.setLayout(self.main_layout)

    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.parent = parent
        self.item = item
        self.setObjectName("productdetail_tab")
        self.product_info = item
        self.search_promo_num = 4
        self.promo_lists = []
        self.init_ui()

    def update_page(self, product_info, promo_list):
        if not promo_list:
            item = {"title": "Medical data from NHIS", "none": "none"}
            self.get_promotion(item)
        else:
            for i in range(self.search_promo_num):
                self.promo_lists.append(Product2(self, promo_list[i], 'simple'))
        self.product_info = product_info
        self.init_ui()

    def get_promotion(self, item=None):
        for i in range(self.search_promo_num):
            self.promo_lists.append(Product(self, item, "simple"))

    def init_ui(self):
        self.comment_list = []
        self.title_label = QLabel(self.product_info["title"])
        self.title_label.setObjectName("title_label")
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.seller_avatar = QLabel("")
        self.seller_avatar.setObjectName("seller_avatar")

        self.seller_name = QLabel("Jade Smile")
        self.seller_name.setObjectName("seller_name")

        self.sales_label = QLabel("Sales: {}".format(self.product_info['sales_number']))
        self.sales_label.setObjectName("sales_label")

        self.size_label = QLabel("Size: {}".format(self.product_info["size"]))
        self.size_label.setObjectName("size_label")

        self.description_label = QLabel("Description")
        self.description_label.setObjectName("description_label")

        self.rating_label = QLabel("Rating")
        self.rating_label.setObjectName("rating_label")

        self.average_score = QLabel("{0}".format(self.product_info["avg_rating"]))
        self.average_score.setObjectName("average_score")

        self.may_like_label = QLabel("You may like")
        self.may_like_label.setObjectName("may_like_label")

        self.data_label = QLabel(self.product_info["created"])
        self.data_label.setObjectName("data_label")

        self.descriptiondetail = QLabel(self.product_info["description"])
        self.descriptiondetail.setObjectName("descriptiondetail")
        self.descriptiondetail.setWordWrap(True)
        self.descriptiondetail.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.price_label = QLabel("${}".format(self.product_info["price"]))
        self.price_label.setObjectName("price_label")

        self.tag = self.item['tags']
        self.tag_num = len(self.tag)
        self.tag_btn_list = []
        for i in range(self.tag_num):
            self.tag_btn_list.append(QPushButton(self.tag[i], self))
            self.tag_btn_list[i].setObjectName("tag_btn_{0}".format(i))
            self.tag_btn_list[i].setProperty("t_value", 1)
            self.tag_btn_list[i].setCursor(QCursor(Qt.PointingHandCursor))

        self.seller_btn = QPushButton(self)
        self.seller_btn.setObjectName("seller_btn")
        self.seller_btn.setText("Christopher Chak")
        self.seller_btn.clicked.connect(self.seller_clicked_act)
        self.seller_btn.setCursor(QCursor(Qt.PointingHandCursor))

        self.comment_btn = QPushButton(self)
        self.comment_btn.setObjectName("comment_btn")
        self.comment_btn.setText("Comment")
        self.comment_btn.clicked.connect(self.handle_comment)
        self.comment_btn.setCursor(QCursor(Qt.PointingHandCursor))

        self.collect_btn = QPushButton(self)
        self.collect_btn.setObjectName("collect_btn")
        self.collect_btn.setText("Collect")
        self.collect_btn.clicked.connect(self.handle_collect)
        self.collect_btn.setCursor(QCursor(Qt.PointingHandCursor))

        self.buynow_btn = QPushButton(self)
        self.buynow_btn.setObjectName("buynow_btn")
        self.buynow_btn.setText("Buy Now")
        self.buynow_btn.clicked.connect(self.handle_buynow)
        self.buynow_btn.setCursor(QCursor(Qt.PointingHandCursor))


        self.frame = QFrame()
        self.frame.setObjectName("rating_frame")

        self.hline_1 = HorizontalLine(self, 2)
        self.hline_2 = HorizontalLine(self, 2)

        self.content_layout = QHBoxLayout(self)
        self.product_layout = QGridLayout(self)
        self.tag_layout = QHBoxLayout(self)
        self.btn_layout = QHBoxLayout(self)
        self.rating_all = QVBoxLayout(self)
        self.comment_layout = QVBoxLayout(self)
        self.promotion_layout = QVBoxLayout(self)
        self.rating_layout = QHBoxLayout(self)


        def get_promotion(item=None):
            for i in range(self.search_promo_num):
                self.promo_lists.append(Product(self, item, "simple"))

        @inlineCallbacks
        def get_product_info():
            promo_list = yield wallet.market_client.query_promotion()
            if not promo_list:
                item = {"title": "Medical data from NHIS", "none": "none"}
                get_promotion(item)
            else:
                for i in range(self.search_promo_num):
                    if i == len(promo_list) - 1:
                        break
                    self.promo_lists.append(Product2(self, promo_list[i], 'simple'))
            comments = yield wallet.market_client.query_comment_by_hash(self.item['msg_hash'])
            comment_size = len(comments)
            for j in range(comment_size):
                self.comment_list.append(ProductDetailTab.ProductComment(self, comments[j]))
            set_layout()
        get_product_info()

        def set_layout():

            # self.content_layout = QHBoxLayout(self)
            self.content_layout.addSpacing(0)

            # self.product_layout = QGridLayout(self)
            self.product_layout.setSpacing(10)
            self.product_layout.setContentsMargins(30, 50, 10, 10)

            self.product_layout.addWidget(self.title_label, 1, 1, 1, 10)
            self.product_layout.addWidget(self.seller_avatar, 2, 1, 1, 1)
            self.product_layout.addWidget(self.seller_btn, 2, 2, 1, 1)
            self.product_layout.addWidget(self.data_label, 2, 3, 1, 2)
            self.product_layout.addWidget(self.size_label, 4, 1, 1, 2)
            self.product_layout.addWidget(self.sales_label, 4, 3, 1, 2)

            # self.tag_layout = QHBoxLayout(self)
            for i in range(self.tag_num):
                self.tag_layout.addWidget(self.tag_btn_list[i])
                self.tag_layout.addSpacing(5)

            self.tag_layout.addStretch(1)

            self.product_layout.addLayout(self.tag_layout, 5, 1, 1, 10)
            self.product_layout.addWidget(self.description_label, 6, 1, 1, 2)
            self.product_layout.addWidget(self.descriptiondetail, 7, 1, 3, 10)
            self.product_layout.addWidget(self.price_label, 9, 1, 1, 2)

            # self.btn_layout = QHBoxLayout(self)
            self.btn_layout.addWidget(self.collect_btn)
            self.btn_layout.addSpacing(12)
            self.btn_layout.addWidget(self.buynow_btn)
            self.btn_layout.addSpacing(12)
            self.btn_layout.addWidget(self.comment_btn)
            self.product_layout.addLayout(self.btn_layout, 10, 1, 1, 6)

            # self.rating_all = QVBoxLayout(self)
            # self.rating_layout = QHBoxLayout(self)
            self.rating_layout.addWidget(self.rating_label)
            self.rating_layout.addStretch(1)
            self.rating_layout.addWidget(self.average_score)

            self.rating_all.addLayout(self.rating_layout)
            self.rating_all.addWidget(self.hline_1)
            self.product_layout.addLayout(self.rating_all, 12, 1, 1, 10)

            # self.comment_layout = QVBoxLayout(self)
            for i in range(len(self.comment_list)):
                self.comment_layout.addWidget(self.comment_list[i])
                self.comment_layout.addSpacing(0)
            self.product_layout.addLayout(self.comment_layout, 14, 1, 3, 10)

            # self.promotion_layout = QVBoxLayout(self)
            self.promotion_layout.setContentsMargins(20, 25, 10, 10)
            self.promotion_layout.addSpacing(0)
            self.promotion_layout.addWidget(self.may_like_label)
            self.promotion_layout.addSpacing(5)
            self.promotion_layout.addWidget(self.hline_2)
            self.promotion_layout.addSpacing(0)
            for i in range(self.search_promo_num):
                if i == len(self.promo_lists) - 1:
                    break
                self.promotion_layout.addWidget(self.promo_lists[i])
                self.promotion_layout.addSpacing(0)

            self.promotion_layout.addStretch(1)

            self.content_layout.addLayout(self.product_layout, 2)
            self.content_layout.addLayout(self.promotion_layout, 1)

            self.setLayout(self.content_layout)
            load_stylesheet(self, "prductdetail.qss")

    def handle_collect(self):
        if self.collect_btn.text() == "Collect":
            fs.add_record_collect(self.product_info)
            self.collect_btn.setText("Collected")

        tab_index = main_wnd.main_tab_index['collect_tab']
        main_wnd.content_tabs.removeTab(tab_index)
        for key in main_wnd.main_tab_index:
            if main_wnd.main_tab_index[key] > tab_index:
                main_wnd.main_tab_index[key] -= 1
        tab_index = main_wnd.content_tabs.addTab(CollectedTab(main_wnd.content_tabs), "")
        main_wnd.main_tab_index['collect_tab'] = tab_index

    def handle_buynow(self):
        BuyNowDialog(self, self.product_info)

    def seller_clicked_act(self):
        wid = main_wnd.content_tabs.findChild(QWidget, "sellerHP_tab")
        main_wnd.content_tabs.setCurrentWidget(wid)

    class CommentDialog(QDialog):
        def __init__(self, parent=None, market_hash=""):
            super().__init__(parent)
            self.parent = parent
            self.market_hash = market_hash
            self.comment_content = self.comment_edit.toPlainText()
            self.resize(300, 400)
            self.setObjectName("comment_dialog")
            self.init_ui()

        def init_ui(self):

            self.comment_label = QLabel("Please input your comment here:")

            self.comment_edit = QTextEdit()
            self.comment_edit.setObjectName("comment_edit")

            self.cancel_btn = QPushButton(self)
            self.cancel_btn.setObjectName("comment_cancel_btn")
            self.cancel_btn.setText("Cancel")
            self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
            self.cancel_btn.clicked.connect(self.handle_cancel)

            self.confirm_btn = QPushButton(self)
            self.confirm_btn.setObjectName("pinfo_publish_btn")
            self.confirm_btn.setText("OK")
            self.confirm_btn.setCursor(QCursor(Qt.PointingHandCursor))
            self.confirm_btn.clicked.connect(self.handle_confirm)

            self.main_layout = QVBoxLayout()
            self.main_layout.addSpacing(0)
            self.main_layout.addWidget(self.comment_label)
            self.main_layout.addSpacing(2)
            self.main_layout.addWidget(self.comment_edit)
            self.main_layout.addSpacing(2)

            self.button_layout = QHBoxLayout()
            self.button_layout.addSpacing(2)
            self.button_layout.addWidget(self.cancel_btn)
            self.button_layout.addSpacing(2)
            self.button_layout.addWidget(self.confirm_btn)

            self.main_layout.addLayout(self.button_layout)

            self.setLayout(self.main_layout)

            logger.debug("Loading stylesheet of comment dialog")
            self.show()

        def handle_confirm(self):
            self.comment_content = self.comment_edit.toPlainText()
            if self.comment_content:
                d_status = wallet.market_client.add_comment_by_hash(self.market_hash, self.comment_content)
                def handle_state(status):
                    if status == 1:
                        QMessageBox.information(self, "Tips", "Comment successfully!")
                    else:
                        QMessageBox.information(self, "Tips", "Failed to comment the products !")
                d_status.addCallback(handle_state)
                self.close()
            else:
                QMessageBox.warning(self, "Warning", "No comment provided!")
                self.close()

        def handle_cancel(self):
            self.close()


    def handle_comment(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
        else:
            market_hash = self.product_info['msg_hash']
            comment_dlg = ProductDetailTab.CommentDialog(self, market_hash)
            comment_dlg.show()


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


class SecurityTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("securitypage")
        self.init_ui()

    def init_ui(self):
        self.balance_label = balance_label = QLabel("Account Balance:")
        balance_label.setObjectName("balance_label")
        self.password_label = password_label = QLabel("Payment Password:")
        password_label.setObjectName("password_label")
        self.accountbinding_label = accountbinding_label = QLabel("Account Binding:")
        accountbinding_label.setObjectName("accountbinding_label")
        self.paylimit_label = paylimit_label = QLabel("Daily Payment Limit:")
        paylimit_label.setObjectName("paylimit_label")

        balance = 9999
        self.balance_value = balance_value = QLabel("{} CPC".format(balance))
        balance_label.setObjectName("balance_label")

        bindingaccout = str("Barack Obama")
        self.binding_label = binding_label = QLabel("{} Account".format(bindingaccout))
        binding_label.setObjectName("binding_label")

        self.cpc_label = cpc_label = QLabel("CPC")
        cpc_label.setObjectName("cpc_label")

        self.password_edit = password_edit = QLineEdit()
        password_edit.setObjectName("password_edit")
        password_edit.setEchoMode(QLineEdit.Password)

        self.paylimit_edit = paylimit_edit = QLineEdit()
        paylimit_edit.setObjectName("paylimit_edit")

        self.display_btn = display_btn = QPushButton("Display Balance")
        self.display_btn.setObjectName("display_btn")
        self.display_btn.clicked.connect(self.handle_display)
        self.reset_btn = reset_btn = QPushButton("Reset Password")
        self.reset_btn.setObjectName("reset_btn")

        self.reset_btn.clicked.connect(self.handle_reset)

        self.security_layout = security_layout = QGridLayout(self)
        self.security_layout.setContentsMargins(40, 40, 150, 300)
        self.security_layout.addWidget(balance_label, 1, 1, 1, 1)

        self.balance_layout = balance_layout = QVBoxLayout(self)
        self.balance_layout.addStretch(1)
        self.balance_layout.addWidget(balance_value)
        self.balance_layout.addSpacing(10)
        self.balance_layout.addWidget(display_btn)
        self.balance_layout.addStretch(2)

        self.security_layout.addLayout(balance_layout, 1, 3, 2, 4)

        self.security_layout.addWidget(password_label, 3, 1, 1, 1)
        self.security_layout.addWidget(password_edit, 3, 3, 1, 5)
        self.security_layout.addWidget(reset_btn, 4, 3, 1, 2)

        self.security_layout.addWidget(accountbinding_label, 5, 1, 1, 1)
        self.security_layout.addWidget(binding_label, 5, 3, 1, 2)
        self.security_layout.addWidget(paylimit_label, 6, 1, 1, 1)
        self.security_layout.addWidget(paylimit_edit, 6, 3, 1, 2)
        self.security_layout.addWidget(cpc_label, 6, 5, 1, 2)

        self.setLayout(security_layout)
        load_stylesheet(self, "security.qss")

    def handle_display(self):
        pass

    def handle_reset(self):
        pass


class PreferenceTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("preferencepage")
        self.init_ui()

    def init_ui(self):
        self.downloadpath_label = downloadpath_label = QLabel("Download Path:")
        downloadpath_label.setObjectName("downloadpath_label")
        self.tips_label = tips_label = QLabel("Send message in these conditions:")
        tips_label.setObjectName("tips_label")
        self.messageset_label = messageset_label = QLabel("Message Setting:")
        messageset_label.setObjectName("messageset_label")
        self.tag_label = tag_label = QLabel("Following Tags:")
        tag_label.setObjectName("tag_label")
        self.seller_label = seller_label = QLabel("Following Sellers:")
        seller_label.setObjectName("seller_label")

        self.downloadpath_edit = downloadpath_edit = QLineEdit()
        downloadpath_edit.setObjectName("downloadpath_edit")

        self.tag = ["tag1", "tag2", "tag3", "tag4"]
        self.tag_num = 4
        self.tag_btn_list = []
        for i in range(self.tag_num):
            self.tag_btn_list.append(QPushButton(self.tag[i], self))
            self.tag_btn_list[i].setObjectName("tag_btn_{0}".format(i))
            self.tag_btn_list[i].setProperty("t_value", 1)
            self.tag_btn_list[i].setCursor(QCursor(Qt.PointingHandCursor))

        self.seller_list = []
        self.seller_follow_number = 2

        def get_seller_list():
            for i in range(self.seller_follow_number):
                self.seller_list.append(Seller(self))

        get_seller_list()

        self.sellerid = {"name": "Chak", "sales": "2020"}
        self.openpath_btn = openpath_btn = QPushButton(self)
        self.openpath_btn.setObjectName("openpath_btn")
        self.openpath_btn.setText("Open...")
        self.openpath_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.openpath_btn.clicked.connect(self.handle_openpath)

        self.addtag_btn = addtag_btn = QPushButton(self)
        self.addtag_btn.setObjectName("addtag_btn")
        self.addtag_btn.setText("Add...")
        self.addtag_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.addtag_btn.clicked.connect(self.handle_addtag)

        self.messageset_checkbox_1 = messageset_checkbox_1 = QCheckBox(self)
        self.messageset_checkbox_1.setObjectName("messageset_checkbox_1")
        self.messageset_checkbox_1.setText("New Order")

        self.messageset_checkbox_2 = messageset_checkbox_2 = QCheckBox(self)
        self.messageset_checkbox_2.setObjectName("messageset_checkbox_2")
        self.messageset_checkbox_2.setText("Account spending")

        self.messageset_checkbox_3 = messageset_checkbox_3 = QCheckBox(self)
        self.messageset_checkbox_3.setObjectName("messageset_checkbox_3")
        self.messageset_checkbox_3.setText("Download failed")

        product_counter = 20
        self.seller_avatar = seller_avatar = QLabel("ICONHERE")
        seller_avatar.setObjectName("seller_avatar")
        self.seller_id = seller_id = QLabel("Christopher Chak")
        seller_id.setObjectName("seller_id")
        self.seller_pcount = seller_pcount = QLabel("Products {}".format(product_counter))
        seller_pcount.setObjectName("seller_pcount")
        self.unfollow_btn = QPushButton("Unfollow")
        self.unfollow_btn.setObjectName("unfollow_btn")
        self.unfollow_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.unfollow_btn.clicked.connect(self.handle_unfollow)


        self.pinfo_preference_layout = pinfo_preference_layout = QGridLayout(self)
        #self.pinfo_top_layout.setSpacing(10)
        self.pinfo_preference_layout.setContentsMargins(40, 40, 150, 100)
        self.pinfo_preference_layout.addWidget(downloadpath_label, 1, 1, 1, 1)
        self.pinfo_preference_layout.addWidget(downloadpath_edit, 1, 3, 1, 10)
        self.pinfo_preference_layout.addWidget(openpath_btn, 2, 3, 1, 2)

        self.pinfo_preference_layout.addWidget(messageset_label, 3, 1, 1, 1)
        self.pinfo_preference_layout.addWidget(tips_label, 3, 3, 1, 5)
        self.pinfo_preference_layout.addWidget(messageset_checkbox_1, 4, 3, 1, 2)
        self.pinfo_preference_layout.addWidget(messageset_checkbox_2, 5, 3, 1, 2)
        self.pinfo_preference_layout.addWidget(messageset_checkbox_3, 6, 3, 1, 2)

        self.pinfo_preference_layout.addWidget(tag_label, 7, 1, 1, 1)
        self.pinfo_tag_layout = pinfo_tag_layout = QHBoxLayout(self)
        for i in range(self.tag_num):
            self.pinfo_tag_layout.addWidget(self.tag_btn_list[i])
            self.pinfo_tag_layout.addSpacing(5)

        self.pinfo_tag_layout.addStretch(1)
        self.pinfo_preference_layout.addLayout(pinfo_tag_layout, 7, 3, 1, 10)
        self.pinfo_preference_layout.addWidget(addtag_btn, 8, 3, 1, 2)

        self.pinfo_preference_layout.addWidget(seller_label, 9, 1, 1, 1)

        self.seller_layout = seller_layout = QVBoxLayout(self)

        for i in range(self.seller_follow_number):
            self.seller_layout.addWidget(self.seller_list[i])
            self.seller_layout.addSpacing(0)

        self.pinfo_preference_layout.addLayout(seller_layout, 9, 3, 5, 6)
        self.setLayout(pinfo_preference_layout)
        load_stylesheet(self, "preference.qss")

    def handle_openpath(self):
        pass

    def handle_addtag(self):
        pass

    def handle_unfollow(self):
        pass


class PersonalInfoPage(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("PersonalInfoPage")
        self.init_ui()

    def init_ui(self):
        self.avatar_label = avatar_label = QLabel("Avatar")
        avatar_label.setObjectName("avatar_label")
        self.avatar_icon = avatar_icon = QLabel("ICONHERE")
        avatar_icon.setObjectName("avatar_icon")
        self.username_label = username_label = QLabel("Username:")
        username_label.setObjectName("username_label")
        self.email_label = email_label = QLabel("Email:")
        email_label.setObjectName("email_label")
        self.gender_label = gender_label = QLabel("Gender:")
        gender_label.setObjectName("gender_label")
        self.phone_label = phone_label = QLabel("Mobile Phone")
        phone_label.setObjectName("phone_label")

        self.username_edit = username_edit = QLineEdit()
        username_edit.setObjectName("username_edit")
        self.email_edit = email_edit = QLineEdit()
        email_edit.setObjectName("email_edit")
        self.phone_edit = phone_edit = QLineEdit()
        phone_edit.setObjectName("phone_edit")


        self.avataripload_btn = avataripload_btn = QPushButton(self)
        self.avataripload_btn.setObjectName("avataripload_btn")
        self.avataripload_btn.setText("Upload/Save")
        self.avataripload_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.avataripload_btn.clicked.connect(self.handle_submit)

        self.gender_btn = gender_btn = QPushButton(self)
        self.gender_btn.setObjectName("gender_btn")

        self.submit_btn = submit_btn = QPushButton(self)
        self.submit_btn.setObjectName("submit_btn")
        self.submit_btn.setText("Submit")
        self.submit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.submit_btn.clicked.connect(self.handle_submit)

        self.gender_menu = gender_menu = QMenu('Gender', self)
        self.male_act = QAction('Male', self)
        self.male_act.triggered.connect(self.set_male_act)
        self.female_act = QAction('Female', self)
        self.female_act.triggered.connect(self.set_female_act)
        self.others_act = QAction('Other', self)
        self.others_act.triggered.connect(self.set_other_act)
        gender_menu.addAction(self.male_act)
        gender_menu.addAction(self.female_act)
        gender_menu.addAction(self.others_act)
        self.gender_btn.setMenu(self.gender_menu)
        self.pinfo_top_layout = pinfo_top_layout = QGridLayout(self)
        self.pinfo_top_layout.setContentsMargins(40, 40, 300, 100)
        self.pinfo_top_layout.addWidget(avatar_label, 1, 1, 1, 1)
        self.pinfo_top_layout.addWidget(avatar_icon, 1, 3, 3, 3)
        self.pinfo_top_layout.addWidget(avataripload_btn, 4, 3, 1, 1)
        self.pinfo_top_layout.addWidget(username_label, 5, 1, 1, 1)
        self.pinfo_top_layout.addWidget(username_edit, 5, 3, 1, 5)
        self.pinfo_top_layout.addWidget(email_label, 6, 1, 1, 1)
        self.pinfo_top_layout.addWidget(email_edit, 6, 3, 1, 20)
        self.pinfo_top_layout.addWidget(gender_label, 7, 1, 1, 1)
        self.pinfo_top_layout.addWidget(gender_btn, 7, 3, 1, 1)
        self.pinfo_top_layout.addWidget(phone_label, 8, 1, 1, 1)
        self.pinfo_top_layout.addWidget(phone_edit, 8, 3, 1, 20)
        self.pinfo_top_layout.addWidget(submit_btn, 10, 3, 1, 2)
        self.setLayout(pinfo_top_layout)
        load_stylesheet(self, "personalinfotab.qss")
    def set_male_act(self):
        self.gender_btn.setText("Male")
    def set_female_act(self):
        self.gender_btn.setText("Female")
    def set_other_act(self):
        self.gender_btn.setText("Other")
    def handle_submit(self):
        pass

class CollectedTab(QScrollArea):
    class SearchBar(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.init_ui()

        def init_ui(self):
            self.file_list = []
            self.setObjectName("search_bar")
            self.setFixedSize(300, 25)
            self.setTextMargins(25, 0, 20, 0)

            self.search_btn = search_btn = QPushButton(self)
            search_btn.setObjectName("search_btn")
            search_btn.setFixedSize(18, 18)
            search_btn.setCursor(QCursor(Qt.PointingHandCursor))

            main_layout = QHBoxLayout()
            main_layout.addWidget(search_btn)
            main_layout.addStretch()
            main_layout.setContentsMargins(5, 0, 0, 0)
            self.setLayout(main_layout)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("collect_tab")
        self.file_list = []
        self.check_list = []
        self.purchased_total_orders = 103
        self.num_file = 100
        self.cur_clicked = 0
        self.check_record_list = []
        self.checkbox_list = []
        self.init_ui()

    def update_table(self):
        print("Updating file list......")
        self.file_list = file_list = fs.get_collect_list()

        for cur_row in range(self.row_number):
            if cur_row == len(file_list):
                break
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Unchecked)
            self.file_table.setItem(cur_row, 0, checkbox_item)
            self.file_table.setItem(cur_row, 1, QTableWidgetItem(file_list[cur_row].name))
            self.file_table.setItem(cur_row, 2, QTableWidgetItem(str(file_list[cur_row].price)))
            self.file_table.setItem(cur_row, 3, QTableWidgetItem(sizeof_fmt(file_list[cur_row].size)))

    def init_ui(self):

        self.uncollect_btn = uncollect_btn = QPushButton("Uncollect")
        uncollect_btn.setObjectName("uncollect_btn")

        self.time_rank_label = time_rank_label = QLabel("Time")
        time_rank_label.setObjectName("time_rank_label")

        self.uncollect_btn.clicked.connect(self.handle_uncollect)
        self.search_bar = PurchasedDownloadedTab.SearchBar(self)

        self.row_number = 100
        self.file_table = TableWidget(self)
        def create_file_table():
            file_table = self.file_table

            file_table.horizontalHeader().setStretchLastSection(True)
            file_table.verticalHeader().setVisible(False)
            file_table.setShowGrid(False)
            file_table.setAlternatingRowColors(True)
            file_table.resizeColumnsToContents()
            file_table.resizeRowsToContents()
            file_table.setFocusPolicy(Qt.NoFocus)
            file_table.horizontalHeader().setHighlightSections(False)
            file_table.setColumnCount(5)
            file_table.setRowCount(self.row_number)
            file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            file_table.setHorizontalHeaderLabels(['', 'Product Name', 'Price', 'Size', ''])
            file_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            file_table.horizontalHeader().setFixedHeight(35)
            file_table.setSortingEnabled(True)

            self.file_list = file_list = fs.get_collect_list()
            # self.check_record_list = []
            # self.checkbox_list = []
            for cur_row in range(self.row_number):
                if cur_row == len(file_list):
                    break
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                self.file_table.setItem(cur_row, 0, checkbox_item)
                self.file_table.setItem(cur_row, 1, QTableWidgetItem(file_list[cur_row].name))
                self.file_table.setItem(cur_row, 2, QTableWidgetItem(str(file_list[cur_row].price)))
                self.file_table.setItem(cur_row, 3, QTableWidgetItem(sizeof_fmt(file_list[cur_row].size)))

                hidden_item = QTableWidgetItem()
                hidden_item.setData(Qt.UserRole, str(self.file_list[cur_row].id))
                self.file_table.setItem(cur_row, 4, hidden_item)

                self.check_record_list.append(False)

        create_file_table()
        self.file_table.sortItems(2)
        self.file_table.horizontalHeader().setStyleSheet("QHeaderView::section{background: #f3f3f3; border: 1px solid #dcdcdc}")
        def record_check(item):
            self.cur_clicked = item.row()
            if item.checkState() == Qt.Checked:
                self.check_record_list[item.row()] = True

        self.file_table.itemClicked.connect(record_check)

        self.main_layout = main_layout = QVBoxLayout(self)
        main_layout.addSpacing(0)
        self.collection_upper_layout = QHBoxLayout(self)
        self.collection_upper_layout.addSpacing(5)
        self.collection_upper_layout.addWidget(self.search_bar)
        self.collection_upper_layout.addSpacing(5)
        self.collection_upper_layout.addWidget(self.time_rank_label)
        self.collection_upper_layout.addStretch(1)
        self.collection_upper_layout.addWidget(self.uncollect_btn)
        self.collection_upper_layout.addSpacing(10)
        self.main_layout.addLayout(self.collection_upper_layout)
        self.main_layout.addSpacing(2)
        self.main_layout.addWidget(self.file_table)
        self.main_layout.addSpacing(2)
        self.setLayout(self.main_layout)
        load_stylesheet(self, "collection.qss")
    def handle_uncollect(self):
        for i in range(len(self.check_record_list)):
            if self.check_record_list[i] is True:
                self.file_table.removeRow(i)
                file_id = self.file_table.item(i, 4).data(Qt.UserRole)
                fs.delete_collect_id(file_id)
class PurchasedTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("purchase_tab")
        self.init_ui()
    def init_ui(self):
        self.purchased_dled_tab_btn = QPushButton("Downloaded")
        self.purchased_dled_tab_btn.setObjectName("purchased_dled_tab_btn")
        self.purchased_dling_tab_btn = QPushButton("Downloading")
        self.purchased_dling_tab_btn.setObjectName("purchased_dling_tab_btn")
        self.purchased_main_tab = purchased_main_tab = QTabWidget(self)
        purchased_main_tab.setObjectName("purchased_main_tab")
        purchased_main_tab.tabBar().hide()
        purchased_main_tab.addTab(PurchasedDownloadedTab(purchased_main_tab), "")
        purchased_main_tab.addTab(PurchasedDownloadingTab(purchased_main_tab), "")
        def dled_btn_clicked():
            self.purchased_main_tab.setCurrentIndex(0)
            self.purchased_dled_tab_btn.setStyleSheet("QPushButton{ padding-left: 14px; padding-right: 14px; border: 1px solid #3173d8; border-top-left-radius: 5px; border-bottom-left-radius: 5px; color: #ffffff; min-height: 30px; max-height: 30px; background: #3173d8; }")
            self.purchased_dling_tab_btn.setStyleSheet("QPushButton{ padding-left: 14px; padding-right: 14px; border: 1px solid #3173d8; border-top-right-radius: 5px; border-bottom-right-radius: 5px; color: #3173d8; min-height: 30px; max-height: 30px; background: #ffffff; }")
        self.purchased_dled_tab_btn.clicked.connect(dled_btn_clicked)
        def dling_btn_clicked():
            self.purchased_main_tab.setCurrentIndex(1)
            self.purchased_dling_tab_btn.setStyleSheet("QPushButton{ padding-left: 14px; padding-right: 14px; border: 1px solid #3173d8; border-top-right-radius: 5px; border-bottom-right-radius: 5px; color: #ffffff; min-height: 30px; max-height: 30px; background: #3173d8; }")
            self.purchased_dled_tab_btn.setStyleSheet("QPushButton{ padding-left: 14px; padding-right: 14px; border: 1px solid #3173d8; border-top-left-radius: 5px; border-bottom-left-radius: 5px; color: #3173d8; min-height: 30px; max-height: 30px; background: #ffffff; }")
        self.purchased_dling_tab_btn.clicked.connect(dling_btn_clicked)

        self.purchased_main_layout = QVBoxLayout(self)
        self.purchased_switch_layout = QHBoxLayout(self)
        self.purchased_switch_layout.setContentsMargins(0, 0, 0, 0)
        self.purchased_switch_layout.setSpacing(0)
        self.purchased_switch_layout.addStretch(1)
        self.purchased_switch_layout.addWidget(self.purchased_dled_tab_btn)
        self.purchased_switch_layout.addWidget(self.purchased_dling_tab_btn)
        self.purchased_switch_layout.addStretch(1)
        self.purchased_main_layout.addLayout(self.purchased_switch_layout)
        self.purchased_main_layout.addSpacing(5)
        self.purchased_main_layout.addWidget(self.purchased_main_tab)
        self.setLayout(self.purchased_main_layout)
        load_stylesheet(self, "purchased.qss")

class PurchasedDownloadedTab(QScrollArea):
    class SearchBar(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.init_ui()
        def init_ui(self):
            self.setObjectName("search_bar")
            self.setFixedSize(300, 25)
            self.setTextMargins(25, 0, 20, 0)

            self.search_btn_cloud = search_btn_cloud = QPushButton(self)
            search_btn_cloud.setObjectName("search_btn")
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
        self.setObjectName("purchased_downloaded_tab")
        self.file_list = []
        self.check_list = []
        self.purchased_total_orders = 0
        self.num_file = 100
        self.cur_clicked = 0
        self.checkbox_list = []
        self.file_table = TableWidget(self)
        self.check_record_list = []
        self.init_ui()
    def update_table(self):
        self.file_list = file_list = fs.get_buyer_file_list()
        for cur_row in range(self.row_number):
            if cur_row == len(file_list):
                break
            if not file_list[cur_row].is_downloaded:
                break
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Unchecked)
            self.file_table.setItem(cur_row, 0, checkbox_item)
            self.file_table.setItem(cur_row, 1, QTableWidgetItem(file_list[cur_row].file_title))
            self.file_table.setItem(cur_row, 2, QTableWidgetItem(sizeof_fmt(file_list[cur_row].size)))
            self.file_table.setItem(cur_row, 3, QTableWidgetItem(file_list[cur_row].path))
            self.file_table.setItem(cur_row, 4, QTableWidgetItem(file_list[cur_row].file_uuid))

    def init_ui(self):

        self.purchased_dled_delete_btn = purchased_dled_delete_btn = QPushButton("Delete")
        purchased_dled_delete_btn.setObjectName("purchased_dled_delete_btn")

        self.hline_1 = HorizontalLine(self, 2)

        self.purchased_total_orders_label = purchased_total_orders_label = QLabel("Total Orders: ")
        purchased_total_orders_label.setObjectName("purchased_total_orders_label")
        # self.total_orders_value = total_orders_value = QLabel("{}".format(self.purchased_total_orders))
        # self.total_orders_value.setObjectName("total_orders_value")
        self.purchased_dled_delete_btn.clicked.connect(self.handle_delete)
        self.search_bar = PurchasedDownloadedTab.SearchBar(self)
        self.time_label = time_label = QLabel("Time")
        time_label.setObjectName("time_label")
        self.open_path = open_path = QLabel("Open file path...")
        open_path.setObjectName("open_path")
        self.row_number = 100

        def create_file_table():
            file_table = self.file_table
            file_table.horizontalHeader().setStretchLastSection(True)
            file_table.verticalHeader().setVisible(False)
            file_table.setShowGrid(False)
            file_table.setAlternatingRowColors(True)
            file_table.resizeColumnsToContents()
            file_table.resizeRowsToContents()
            file_table.setFocusPolicy(Qt.NoFocus)
            file_table.horizontalHeader().setHighlightSections(False)
            file_table.setColumnCount(5)
            file_table.setRowCount(self.row_number)
            file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            file_table.setHorizontalHeaderLabels(['', 'Product Name', 'Size', 'Path', 'Remote URI'])
            file_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            file_table.horizontalHeader().setFixedHeight(35)
            file_table.verticalHeader().setDefaultSectionSize(30)
            file_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
            file_table.setSortingEnabled(True)
            def right_menu():
                self.downloaded_right_menu = QMenu(self.file_table)
                self.downloaded_open_act = QAction('Open file', self)
                self.downloaded_open_act.triggered.connect(self.handle_open_act)
                self.downloaded_right_menu.addAction(self.downloaded_open_act)
                self.downloaded_right_menu.exec_(QCursor.pos())
            file_table.set_right_menu(right_menu)

            self.file_list = file_list = fs.get_buyer_file_list()
            for cur_row in range(self.row_number):
                if cur_row == len(file_list):
                    break
                if not file_list[cur_row].is_downloaded:
                    continue
                self.purchased_total_orders += 1
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                self.file_table.setItem(cur_row, 0, checkbox_item)
                self.file_table.setItem(cur_row, 1, QTableWidgetItem(file_list[cur_row].file_title))
                self.file_table.setItem(cur_row, 2, QTableWidgetItem(sizeof_fmt(file_list[cur_row].size)))
                self.file_table.setItem(cur_row, 3, QTableWidgetItem(file_list[cur_row].path))
                self.file_table.setItem(cur_row, 4, QTableWidgetItem(file_list[cur_row].file_uuid))
                self.check_record_list.append(False)
        create_file_table()
        self.total_orders_value = QLabel("{}".format(self.purchased_total_orders))
        self.total_orders_value.setObjectName("total_orders_value")
        self.file_table.sortItems(2)
        self.file_table.horizontalHeader().setStyleSheet("QHeaderView::section{background: #f3f3f3; border: 1px solid #dcdcdc}")
        def record_check(item):
            self.cur_clicked = item.row()
            if item.checkState() == Qt.Checked:
                self.check_record_list[item.row()] = True
        self.file_table.itemClicked.connect(record_check)

        self.main_layout = main_layout = QVBoxLayout(self)
        main_layout.addSpacing(0)
        self.main_layout.setContentsMargins(10, 0, 10, 10)
        self.main_layout.addWidget(self.hline_1)
        self.main_layout.addSpacing(0)
        self.purchased_dled_upper_layout = QHBoxLayout(self)
        self.purchased_dled_upper_layout.addSpacing(0)
        self.purchased_dled_upper_layout.addWidget(self.purchased_total_orders_label)
        self.purchased_dled_upper_layout.addSpacing(0)
        self.purchased_dled_upper_layout.addWidget(self.total_orders_value)
        self.purchased_dled_upper_layout.addSpacing(10)
        self.purchased_dled_upper_layout.addWidget(self.search_bar)
        self.purchased_dled_upper_layout.addSpacing(10)
        self.purchased_dled_upper_layout.addWidget(self.time_label)
        self.purchased_dled_upper_layout.addSpacing(10)
        self.purchased_dled_upper_layout.addWidget(self.open_path)
        self.purchased_dled_upper_layout.addStretch(1)
        self.purchased_dled_upper_layout.addWidget(self.purchased_dled_delete_btn)

        self.main_layout.addLayout(self.purchased_dled_upper_layout)
        self.main_layout.addSpacing(2)
        self.main_layout.addWidget(self.file_table)
        self.main_layout.addSpacing(2)
        self.setLayout(self.main_layout)


    def handle_delete(self):
        for i in range(len(self.check_record_list)):
            if self.check_record_list[i] is True:
                file_path = self.file_table.item(i, 3).text()
                fs.delete_buyer_file(file_path)
                self.file_table.removeRow(i)
        self.check_record_list = [False for i in range(self.file_table.rowCount())]

    def handle_open_act(self):
        cur_row = self.cur_clicked
        file_path = self.file_table.item(cur_row, 3).text()
        open_file(file_path)


class DownloadingProgressBar(QProgressBar):

    def __init__(self, cur_row=None):
        super().__init__()
        self.cur_row = cur_row
        self.step = 0
        self.max_step = 0
        self.init_ui()

    def init_ui(self):
        self.setGeometry(30, 40, 200, 25)

        self.timer = QBasicTimer()
        from random import randint
        self.max_step = randint(500, 1000)
        self.timer.start(self.max_step, self)
        self.show()

    def timerEvent(self, e):
        if self.step >= self.max_step:
            self.timer.stop()
            return

        self.step = self.step + 1
        self.setValue(self.step)

    def setRow(self, new_row):
        self.cur_row = new_row

    def isComplete(self):
        return(self.step >= self.max_step)


class PurchasedDownloadingTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("purchased_downloading_tab")
        self.cur_clicked = 0
        self.file_table = TableWidget(self)
        self.file_list = []
        self.check_record_list = []
        self.checkbox_list = []
        self.init_ui()

    def update_table(self):
        file_list = []
        dict_exa = {"name": "Avengers: Infinity War - 2018", "size": "7200", "ordertime": "2018/2/4 08:30",
                    "price": "36"}
        for i in range(self.row_number):
            file_list.append(dict_exa)

        for cur_row in range(self.row_number):
            if cur_row == len(file_list):
                break
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Unchecked)
            dling_progressbar = QProgressBar()
            # dling_progressbar = DownloadingProgressBar()
            dling_progressbar.setFixedSize(150, 8)
            dling_progressbar.setMaximum(100)
            dling_progressbar.setMinimum(0)
            dling_progressbar.setValue(49)
            self.file_table.setItem(cur_row, 0, checkbox_item)
            self.file_table.setItem(cur_row, 1, QTableWidgetItem(file_list[cur_row]["name"]))
            self.file_table.setCellWidget(cur_row, 2, dling_progressbar)
            self.file_table.setItem(cur_row, 3, QTableWidgetItem(file_list[cur_row]["ordertime"]))

    def set_right_menu(self, func):
        self.customContextMenuRequested[QPoint].connect(func)

    def init_ui(self):
        self.actual_row_num = 0
        self.check_list = []
        self.purchased_total_orders = 0
        self.num_file = 100
        self.cur_clicked = 0

        self.purchased_total_orders_label = purchased_total_orders_label = QLabel("Total Orders: ")
        purchased_total_orders_label.setObjectName("purchased_total_orders_label")
        # self.total_orders_value = total_orders_value = QLabel("{}".format(self.purchased_total_orders))
        # self.total_orders_value.setObjectName("total_orders_value")
        self.purchased_dling_delete_btn = purchased_dling_delete_btn = QPushButton("Delete")
        purchased_dling_delete_btn.setObjectName("purchased_dling_delete_btn")
        self.purchased_dling_start_btn = purchased_dling_start_btn = QPushButton("Start")
        purchased_dling_start_btn.setObjectName("purchased_dling_start_btn")
        self.purchased_dling_pause_btn = purchased_dling_pause_btn = QPushButton("Pause")
        purchased_dling_pause_btn.setObjectName("purchased_dling_pause_btn")

        self.purchased_dling_delete_btn.clicked.connect(self.handle_purchased_delete)
        self.open_path = open_path = QLabel("Open file path...")
        open_path.setObjectName("open_path")

        self.row_number = 100

        self.hline_1 = HorizontalLine(self, 2)

        def create_file_table():
            file_table = self.file_table

            def right_menu():
                self.purchased_right_menu = QMenu(file_table)
                self.purchased_delete_act = QAction('Delete', self)
                self.purchased_publish_act = QAction('Publish', self)

                self.purchased_delete_act.triggered.connect(self.handle_delete_act)
                self.purchased_publish_act.triggered.connect(self.handle_publish_act)

                self.purchased_right_menu.addAction(self.purchased_delete_act)
                self.purchased_right_menu.addAction(self.purchased_publish_act)

                self.purchased_right_menu.exec_(QCursor.pos())

            file_table.horizontalHeader().setStretchLastSection(True)
            file_table.verticalHeader().setVisible(False)
            file_table.setShowGrid(False)
            file_table.setAlternatingRowColors(True)
            file_table.resizeColumnsToContents()
            file_table.resizeRowsToContents()
            file_table.setFocusPolicy(Qt.NoFocus)
            file_table.horizontalHeader().setHighlightSections(False)
            file_table.setColumnCount(4)
            file_table.setRowCount(self.row_number)
            file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            file_table.set_right_menu(right_menu)
            file_table.setHorizontalHeaderLabels(['CheckState', 'Product Name', 'Progress', 'File UUID'])
            file_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            file_table.horizontalHeader().setFixedHeight(35)
            file_table.verticalHeader().setDefaultSectionSize(30)
            file_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
            file_table.setSortingEnabled(True)

            self.file_list = file_list = fs.get_buyer_file_list()

            for cur_row in range(self.row_number):
                if cur_row == len(file_list):
                    break
                if file_list[cur_row].is_downloaded is False:
                    self.purchased_total_orders += 1
                    checkbox_item = QTableWidgetItem()
                    checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    checkbox_item.setCheckState(Qt.Unchecked)
                    dling_progressbar = DownloadingProgressBar(cur_row)
                    self.file_table.setItem(cur_row, 0, checkbox_item)
                    self.file_table.setItem(cur_row, 1, QTableWidgetItem(file_list[cur_row].file_title))
                    self.file_table.setCellWidget(cur_row, 2, dling_progressbar)
                    self.file_table.setItem(cur_row, 3, QTableWidgetItem(file_list[cur_row].file_uuid))
                    self.check_record_list.append(False)
                    dling_progressbar.valueChanged.connect(self.handle_complete)

                    self.actual_row_num += 1

        create_file_table()
        self.total_orders_value = QLabel("{}".format(self.purchased_total_orders))
        self.total_orders_value.setObjectName("total_orders_value")

        self.file_table.sortItems(1)
        self.file_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section{background: #f3f3f3; border: 1px solid #dcdcdc}")

        def record_check(item):
            self.cur_clicked = item.row()
            if item.checkState() == Qt.Checked:
                self.check_record_list[item.row()] = True

        self.file_table.itemClicked.connect(record_check)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 0, 10, 10)
        self.main_layout.addSpacing(0)
        self.main_layout.addWidget(self.hline_1)
        self.main_layout.addSpacing(0)
        self.purchased_upper_layout = QHBoxLayout(self)
        self.purchased_upper_layout.addSpacing(0)
        self.purchased_upper_layout.addWidget(self.purchased_total_orders_label)
        self.purchased_upper_layout.addSpacing(0)
        self.purchased_upper_layout.addWidget(self.total_orders_value)
        self.purchased_upper_layout.addSpacing(10)
        self.purchased_upper_layout.addWidget(self.open_path)
        self.purchased_upper_layout.addStretch(1)
        self.purchased_upper_layout.addWidget(self.purchased_dling_start_btn)
        self.purchased_upper_layout.addSpacing(10)
        self.purchased_upper_layout.addWidget(self.purchased_dling_pause_btn)
        self.purchased_upper_layout.addSpacing(10)
        self.purchased_upper_layout.addWidget(self.purchased_dling_delete_btn)
        self.purchased_upper_layout.addSpacing(5)

        self.main_layout.addLayout(self.purchased_upper_layout)
        self.main_layout.addSpacing(2)
        self.main_layout.addWidget(self.file_table)
        self.main_layout.addSpacing(2)
        self.setLayout(self.main_layout)

    def handle_complete(self, item):
        if item >= 100:
            file_title = self.file_table.item(0, 1).text()
            fs.buyer_file_update(file_title)
            self.file_table.setRowCount(0)


    def handle_purchased_delete(self):
        for i in range(len(self.check_record_list)):
            if self.check_record_list[i] is True:
                self.file_table.removeRow(i)


class PublishDialog(QDialog):
    def __init__(self, parent=None, product_id=None, tab='cloud'):
        super().__init__(parent)
        self.parent = parent
        self.tab = tab
        self.resize(300, 400)
        self.setObjectName("publish_dialog")
        self.product_id = product_id

        self.init_ui()

    def init_ui(self):

        #Labels def
        self.setWindowTitle("Publish Product")
        self.pinfo_title_label = pinfo_title_label = QLabel("Title:")
        pinfo_title_label.setObjectName("pinfo_title_label")
        self.pinfo_descrip_label = pinfo_descrip_label = QLabel("Description:")
        pinfo_descrip_label.setObjectName("pinfo_descrip_label")
        self.pinfo_tag_label = pinfo_tag_label = QLabel("Tag:")
        pinfo_tag_label.setObjectName("pinfo_tag_label")
        self.pinfo_price_label = pinfo_price_label = QLabel("Price:")
        pinfo_price_label.setObjectName("pinfo_price_label")
        self.pinfo_cpc_label = pinfo_cpc_label = QLabel("CPC")
        pinfo_cpc_label.setObjectName("pinfo_cpc_label")

        self.pinfo_title_edit = pinfo_title_edit = QLineEdit()
        pinfo_title_edit.setObjectName("pinfo_title_edit")
        self.pinfo_descrip_edit = pinfo_descrip_edit = QTextEdit()
        pinfo_descrip_edit.setObjectName("pinfo_descrip_edit")
        self.pinfo_tag_edit = pinfo_tag_edit = QLineEdit()
        pinfo_tag_edit.setObjectName("pinfo_tag_edit")
        self.pinfo_price_edit = pinfo_price_edit = QLineEdit()
        pinfo_price_edit.setObjectName("pinfo_price_edit")

        self.tag = ["tag1", "tag2", "tag3", "tag4"]
        self.tag_num = 4
        self.tag_btn_list = []
        for i in range(self.tag_num):
            self.tag_btn_list.append(QPushButton(self.tag[i], self))
            self.tag_btn_list[i].setObjectName("tag_btn_{0}".format(i))
            self.tag_btn_list[i].setProperty("t_value", 1)
            self.tag_btn_list[i].setCheckable(True)
            self.tag_btn_list[i].setCursor(QCursor(Qt.PointingHandCursor))

        self.pinfo_cancel_btn = pinfo_cancel_btn = QPushButton(self)
        self.pinfo_cancel_btn.setObjectName("pinfo_cancel_btn")
        self.pinfo_cancel_btn.setText("Cancel")
        self.pinfo_cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.pinfo_cancel_btn.clicked.connect(self.handle_cancel)

        self.pinfo_publish_btn = pinfo_publish_btn = QPushButton(self)
        self.pinfo_publish_btn.setObjectName("pinfo_publish_btn")
        self.pinfo_publish_btn.setText("Publish")
        self.pinfo_publish_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.pinfo_publish_btn.clicked.connect(self.handle_publish)

        self.pinfo_checkbox = pinfo_checkbox = QCheckBox(self)
        self.pinfo_checkbox.setObjectName("pinfo_checkbox")
        self.pinfo_checkbox.setText("I agree with the CPC Agreement")


        def set_layout():
            self.pinfo_top_layout = pinfo_top_layout = QGridLayout(self)
            self.pinfo_top_layout.setContentsMargins(40, 40, 100, 40)
            self.pinfo_top_layout.addWidget(pinfo_title_label, 1, 1, 1, 1)
            self.pinfo_top_layout.addWidget(pinfo_title_edit, 1, 3, 1, 20)
            self.pinfo_top_layout.addWidget(pinfo_descrip_label, 2, 1, 1, 1)
            self.pinfo_top_layout.addWidget(pinfo_descrip_edit, 2, 3, 3, 20)
            self.pinfo_top_layout.addWidget(pinfo_tag_label, 8, 1, 1, 1)
            self.pinfo_tag_layout = pinfo_tag_layout = QHBoxLayout(self)
            for i in range(self.tag_num):
                self.pinfo_tag_layout.addWidget(self.tag_btn_list[i])
                self.pinfo_tag_layout.addSpacing(5)

            self.pinfo_tag_layout.addStretch(1)
            self.pinfo_top_layout.addLayout(pinfo_tag_layout, 8, 3, 1, 10)
            self.pinfo_top_layout.addWidget(pinfo_tag_edit, 9, 3, 1, 3)

            self.pinfo_price_layout = pinfo_price_layout = QHBoxLayout(self)
            self.pinfo_price_layout.addWidget(pinfo_price_edit)
            self.pinfo_price_layout.addSpacing(5)
            self.pinfo_price_layout.addWidget(pinfo_cpc_label)
            self.pinfo_price_layout.addStretch(1)
            self.pinfo_top_layout.addLayout(pinfo_price_layout, 10, 3, 1, 10)
            self.pinfo_top_layout.addWidget(pinfo_price_label, 10, 1, 1, 1)
            self.pinfo_top_layout.addWidget(pinfo_checkbox, 12, 3, 1, 2)

            self.pinfo_btn_layout = pinfo_btn_layout = QHBoxLayout(self)
            self.pinfo_btn_layout.addWidget(pinfo_cancel_btn)
            self.pinfo_btn_layout.addSpacing(80)
            self.pinfo_btn_layout.addWidget(pinfo_publish_btn)
            self.pinfo_btn_layout.addStretch(1)
            self.pinfo_top_layout.addLayout(pinfo_btn_layout, 13, 3, 1, 15)

            self.setLayout(pinfo_top_layout)
        set_layout()
        load_stylesheet(self, "publishdialog.qss")
        self.show()

    def handle_publish(self):
        self.pinfo_title = self.pinfo_title_edit.text()
        self.pinfo_descrip = self.pinfo_descrip_edit.toPlainText()
        self.pinfo_tag = self.pinfo_tag_edit.text()
        self.pinfo_price = self.pinfo_price_edit.text()
        self.pinfo_checkbox_state = self.pinfo_checkbox.isChecked()
        if self.pinfo_title and self.pinfo_descrip and self.pinfo_tag and self.pinfo_price and self.pinfo_checkbox_state:

            file_info = fs.get_file_by_id(self.product_id)
            self.size = file_info.size
            self.start_date = '2018-04-01 10:10:10'
            self.end_date = '2018-04-01 10:10:10'
            self.path = file_info.path
            self.file_md5 = hashlib.md5(open(self.path, "rb").read()).hexdigest()
            logger.debug(self.file_md5)
            d_publish = wallet.market_client.publish_product(self.product_id, self.pinfo_title,
                                                             self.pinfo_descrip, self.pinfo_price,
                                                             self.pinfo_tag, self.start_date,
                                                             self.end_date, self.file_md5, self.size)
            def update_table(market_hash):
                d = wallet.market_client.update_file_info(self.product_id, market_hash)
                def handle_update_file(status):
                    if status == 1:
                        QMessageBox.information(self, "Tips", "Update market side product successfully !")
                        tab_index = main_wnd.main_tab_index['cloud_tab']
                        main_wnd.content_tabs.removeTab(tab_index)
                        for key in main_wnd.main_tab_index:
                            if main_wnd.main_tab_index[key] > tab_index:
                                main_wnd.main_tab_index[key] -= 1
                        tab_index = main_wnd.content_tabs.addTab(CloudTab(main_wnd.content_tabs), "")
                        main_wnd.main_tab_index['cloud_tab'] = tab_index
                        if self.tab == 'cloud':
                            main_wnd.content_tabs.setCurrentIndex(tab_index)

                        tab_index = main_wnd.main_tab_index['selling_tab']
                        main_wnd.content_tabs.removeTab(tab_index)
                        for key in main_wnd.main_tab_index:
                            if main_wnd.main_tab_index[key] > tab_index:
                                main_wnd.main_tab_index[key] -= 1
                        logger.debug("update sell tab")
                        tab_index = main_wnd.content_tabs.addTab(SellTab(main_wnd.content_tabs), "")
                        main_wnd.main_tab_index['selling_tab'] = tab_index
                        if self.tab == 'sell':
                            main_wnd.content_tabs.setCurrentIndex(tab_index)

                        if self.tab != 'cloud' and self.tab != 'sell':
                            QMessageBox.information("Wrong parameters for publishing products!")

                d.addCallback(handle_update_file)

            d_publish.addCallback(update_table)

            self.close()
        else:
            QMessageBox.warning(self, "Warning", "Please fill out the necessary selling information first!")

    def handle_cancel(self):
        print("exiting the current dialog")
        self.close()

class SellTab(QScrollArea):
    class SearchBar(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.init_ui()

        def init_ui(self):
            self.setObjectName("search_bar")
            self.setFixedSize(300, 25)
            self.setTextMargins(25, 0, 20, 0)

            self.search_btn_cloud = search_btn_cloud = QPushButton(self)
            search_btn_cloud.setObjectName("search_btn_sell")
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
        self.setObjectName("selling_tab")
        self.file_list = []

        self.init_ui()

    def update_table(self):

        d = wallet.market_client.query_by_seller(wallet.market_client.public_key)
        def handle_query_by_seller(products):
            self.file_list = []
            if not products:
                item = {"ID": "00x2222", "title": "Medical Data from Mayo Clinic", "price": "100", "avg_rating": "83%", "sales_number": "13087", "end_date": "2018-05-05"}
                for i in range(self.row_number):
                    self.file_list.append(item)
            else:
                self.file_list = products
            set_table_value(self.file_list)

        d.addCallback(handle_query_by_seller)

        def set_table_value(products):
            for cur_row in range(self.row_number):
                if cur_row == len(products):
                    break
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                self.file_table.setItem(cur_row, 0, checkbox_item)
                self.file_table.setItem(cur_row, 1, QTableWidgetItem(products[cur_row]["title"]))
                self.file_table.setItem(cur_row, 2, QTableWidgetItem(str(products[cur_row]["price"])))
                self.file_table.setItem(cur_row, 3, QTableWidgetItem(str(products[cur_row]["sales_number"])))
                self.file_table.setItem(cur_row, 4, QTableWidgetItem(str(products[cur_row]["avg_rating"])))
                self.file_table.setItem(cur_row, 5, QTableWidgetItem(products[cur_row]["end_date"]))

                hidden_item = QTableWidgetItem()
                hidden_item.setData(Qt.UserRole, self.file_list[cur_row]['market_hash'])
                self.file_table.setItem(cur_row, 6, hidden_item)

    def set_right_menu(self, func):
        self.customContextMenuRequested[QPoint].connect(func)

    def handle_upload(self):
        self.local_file = QFileDialog.getOpenFileName()[0]

    def init_ui(self):
        self.frame = QFrame()
        self.frame.setObjectName("sell_frame")
        self.setWidget(self.frame)
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(500)

        self.check_list = []
        self.sell_product = 100
        self.total_orders = 103
        self.total_sales = 1234
        self.cur_clicked = 0

        self.sell_product_label = sell_product_label = QLabel("Products:")
        sell_product_label.setObjectName("sell_product_label")
        self.product_value = product_value = QLabel("{}".format(self.sell_product))
        product_value.setObjectName("product_value")

        self.sell_orders_label = sell_orders_label = QLabel("Total Orders:")
        sell_orders_label.setObjectName("sell_orders_label")
        self.order_value = order_value = QLabel("{}".format(self.total_orders))
        order_value.setObjectName("order_value")

        self.total_sales_label = total_sales_label = QLabel("Total Sales($):")
        total_sales_label.setObjectName("total_sales_label")
        self.sales_value = sales_value = QLabel("{}".format(self.total_sales))
        sales_value.setObjectName("sales_value")
        self.time_rank_label = time_rank_label = QLabel("Time")
        time_rank_label.setObjectName("time_rank_label")
        self.tag_rank_label = tag_rank_label = QLabel("Tag")
        tag_rank_label.setObjectName("tag_rank_label")
        self.sell_delete_btn = sell_delete_btn = QPushButton("Delete")
        sell_delete_btn.setObjectName("sell_delete_btn")
        self.sell_delete_btn.clicked.connect(self.handle_delete)

        self.sell_publish_btn = sell_publish_btn = QPushButton("Publish")
        sell_publish_btn.setObjectName("sell_publish_btn")
        self.sell_publish_btn.clicked.connect(self.handle_publish)


        self.search_bar_sell = SellTab.SearchBar(self)
        self.time_label = QLabel("Time")
        self.row_number = 100


        def create_file_table():
            logger.debug("in create file table")
            self.file_table = file_table = TableWidget(self)

            file_table.horizontalHeader().setStretchLastSection(True)
            file_table.verticalHeader().setVisible(False)
            file_table.setShowGrid(False)
            file_table.setAlternatingRowColors(True)
            file_table.resizeColumnsToContents()
            file_table.resizeRowsToContents()
            file_table.setFocusPolicy(Qt.NoFocus)
            file_table.horizontalHeader().setHighlightSections(False)
            file_table.setColumnCount(7)
            file_table.setRowCount(self.row_number)
            file_table.setSelectionBehavior(QAbstractItemView.SelectRows)

            file_table.setHorizontalHeaderLabels(['', 'Product Name', 'Price ($)', 'Sales', 'Rating', 'Update Time', ''])
            file_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            file_table.horizontalHeader().setFixedHeight(35)
            file_table.verticalHeader().setDefaultSectionSize(30)
            file_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
            file_table.setSortingEnabled(True)

            self.check_record_list = []
            self.checkbox_list = []
            for cur_row in range(self.row_number):
                if cur_row == len(self.file_list):
                    break
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                logger.debug("current row of product: %s", self.file_list[cur_row])
                self.file_table.setItem(cur_row, 0, checkbox_item)
                self.file_table.setItem(cur_row, 1, QTableWidgetItem(self.file_list[cur_row]["title"]))
                self.file_table.setItem(cur_row, 2, QTableWidgetItem(str(self.file_list[cur_row]["price"])))
                self.file_table.setItem(cur_row, 3, QTableWidgetItem(str(self.file_list[cur_row]["sales_number"])))
                self.file_table.setItem(cur_row, 4, QTableWidgetItem(str(self.file_list[cur_row]["avg_rating"])))
                self.file_table.setItem(cur_row, 5, QTableWidgetItem(self.file_list[cur_row]["end_date"]))
                hidden_item = QTableWidgetItem()
                hidden_item.setData(Qt.UserRole, self.file_list[cur_row]['market_hash'])
                self.file_table.setItem(cur_row, 6, hidden_item)
                self.check_record_list.append(False)

        d = wallet.market_client.query_by_seller(wallet.market_client.public_key)
        def handle_query_by_seller(products):
            logger.debug("in handle query by seller")
            logger.debug("seller's product list: %s", products)
            self.file_list = []
            if not products:
                item = {"ID": "00x2222", "title": "Medical Data from Mayo Clinic", "price": "100", "avg_rating": "83%", "sales_number": "13087", "end_date": "2018-05-05"}
                for i in range(self.row_number):
                    self.file_list.append(item)
            else:
                self.file_list = products
            create_file_table()
            self.file_table.itemClicked.connect(record_check)

            self.file_table.sortItems(2)
            self.file_table.horizontalHeader().setStyleSheet("QHeaderView::section{background: #f3f3f3; border: 1px solid #dcdcdc}")
            set_layout()
        d.addCallback(handle_query_by_seller)

        def record_check(item):
            self.cur_clicked = item.row()
            if item.checkState() == Qt.Checked:
                self.check_record_list[item.row()] = True

        def set_layout():
            self.main_layout = main_layout = QVBoxLayout(self)
            main_layout.addSpacing(0)
            self.layout1 = QHBoxLayout(self)
            self.layout1.addSpacing(0)
            self.layout1.addWidget(self.sell_product_label)
            self.layout1.addWidget(self.product_value)
            self.layout1.addSpacing(5)
            self.layout1.addWidget(self.sell_orders_label)
            self.layout1.addWidget(self.order_value)
            self.layout1.addSpacing(5)
            self.layout1.addWidget(self.total_sales_label)
            self.layout1.addWidget(self.sales_value)
            self.layout1.addStretch(1)
            self.main_layout.addLayout(self.layout1)
            self.layout2 = QHBoxLayout(self)
            self.layout2.addWidget(self.search_bar_sell)
            self.layout2.addSpacing(10)
            self.layout2.addWidget(self.time_rank_label)
            self.layout2.addSpacing(10)
            self.layout2.addWidget(self.tag_rank_label)
            self.layout2.addStretch(1)
            self.layout2.addWidget(self.sell_delete_btn)
            self.layout2.addSpacing(5)
            self.layout2.addWidget(self.sell_publish_btn)
            self.layout2.addSpacing(5)
            self.main_layout.addLayout(self.layout2)
            self.main_layout.addSpacing(2)
            self.main_layout.addWidget(self.file_table)
            self.main_layout.addSpacing(2)
            self.setLayout(self.main_layout)
            load_stylesheet(self, "sell.qss")

    def handle_delete(self):
        if wallet.market_client.token == "":
            QMessageBox.information(self, "Tips", "Please login first !")
            return
        for i in range(len(self.check_record_list)):
            if self.check_record_list[i] is True:
                self.file_table.removeRow(i)
                market_hash = self.file_table.item(self.cur_clicked, 6).data(Qt.UserRole)
                d_status = wallet.market_client.hide_product(market_hash)
                def handle_state(status):
                    if status == 1:
                        QMessageBox.information(self, "Tips", "Successfully deleted the product")
                    else:
                        QMessageBox.information(self, "Tips", "Problem occurred when deleting the file")
                d_status.addCallback(handle_state)
        self.check_record_list = [False for i in range(self.file_table.rowCount())]


    def handle_delete_act(self):
        self.file_table.removeRow(self.cur_clicked)

    def handle_publish(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
        else:
            self.file_selection_dlg = SelectionDialog(self)
            print("handle publish act....")

class SelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.resize(300, 400)
        self.setObjectName("selection_dialog")
        self.setWindowTitle("Select which file to publish")
        self.pub_list = []
        self.init_ui()

    def init_ui(self):

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("unpublished_list")
        self.file_list = fs.get_file_list()

        for i in range(len(self.file_list)):
            if not self.file_list[i].is_published:
                self.pub_list.append(self.file_list[i])
                item = QListWidgetItem(self.file_list[i].name)
                self.list_widget.addItem(item)
        self.publish_btn = QPushButton("Publish")
        self.publish_btn.setObjectName("publish_btn")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_btn")

        self.publish_btn.clicked.connect(self.handle_publish)
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
            self.btn_layout.addWidget(self.publish_btn)

            self.main_layout.addLayout(self.btn_layout)
            self.setLayout(self.main_layout)
        set_layout()
        logger.debug("Loading stylesheets of SelectionDialog")
        load_stylesheet(self, "selectiondialog.qss")
        self.show()

    def handle_publish(self):
        cur_row = self.list_widget.currentRow()
        product_id = self.pub_list[cur_row].id
        PublishDialog(self, product_id=product_id, tab='sell')
        self.close()

    def handle_cancel(self):
        self.close()

class FollowingTagTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setObjectName("follow_tab_tag")
        self.init_ui()

    def init_ui(self):
        self.frame = QFrame()
        self.frame.setObjectName("follow_tag_frame")
        self.setWidget(self.frame)
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(500)

        self.follow_item_num = 4
        self.promo_num_max = 3

        self.item_lists = []
        self.promo_lists = []

        d_products = wallet.market_client.query_recommend_product()
        def get_items(products):
            for i in range(self.follow_item_num):
                if i == len(products) - 1:
                    break
                self.item_lists.append(Product2(parent=self, item=products[i]))
            d_promotion = wallet.market_client.query_promotion()
            def get_promotion(products):
                for i in range(self.promo_num_max):
                    if i == len(products) - 1:
                        break
                    self.promo_lists.append(Product2(parent=self, item=products[i], mode="simple"))
                set_layout()
            d_promotion.addCallback(get_promotion)
        d_products.addCallback(get_items)

        def set_layout():
            self.follow_main_layout = QHBoxLayout(self)

            self.follow_tag_product_layout = QVBoxLayout(self)
            self.follow_tag_product_layout.addSpacing(0)

            self.follow_tag_promotion_layout = QVBoxLayout(self)
            self.follow_tag_promotion_layout.addSpacing(0)

            for i in range(self.follow_item_num):
                self.follow_tag_product_layout.addWidget(self.item_lists[i])
                self.follow_tag_product_layout.addSpacing(0)

            self.follow_tag_promotion_layout.addStretch(1)

            self.promo_layout = QVBoxLayout(self)
            self.promo_layout.setContentsMargins(0, 0, 0, 0)
            self.promo_layout.addSpacing(0)
            for i in range(self.promo_num_max):
                self.promo_layout.addWidget(self.promo_lists[i])
                self.promo_layout.addSpacing(0)

            self.promo_layout.addStretch(1)
            self.follow_main_layout.addLayout(self.follow_tag_product_layout, 2)
            self.follow_main_layout.addSpacing(1)
            self.follow_main_layout.addLayout(self.promo_layout, 1)

            self.setLayout(self.follow_main_layout)
        load_stylesheet(self, "followingtag.qss")


class FollowingSellTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("follow_sell_tag")
        self.init_ui()

    def init_ui(self):
        self.frame = QFrame()
        self.frame.setObjectName("follow_sell_frame")
        self.setWidget(self.frame)
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(500)

        self.follow_item_num = 5
        self.promo_num_max = 4

        self.item_lists = []
        self.promo_lists = []


        d_products = wallet.market_client.query_recommend_product()
        def get_items(products):
            for i in range(self.follow_item_num):
                if i == len(products) - 1:
                    break
                self.item_lists.append(Product2(parent=self, item=products[i]))
            d_promotion = wallet.market_client.query_promotion()
            def get_promotion(products):
                for i in range(self.promo_num_max):
                    if i == len(products) - 1:
                        break
                    self.promo_lists.append(Product2(parent=self, item=products[i], mode="simple"))
                set_layout()
            d_promotion.addCallback(get_promotion)
        d_products.addCallback(get_items)

        def set_layout():

            self.follow_main_layout = QHBoxLayout(self)

            self.follow_tag_product_layout = QVBoxLayout(self)
            self.follow_tag_product_layout.addSpacing(0)

            self.follow_tag_promotion_layout = QVBoxLayout(self)
            self.follow_tag_promotion_layout.addSpacing(0)

            for i in range(self.follow_item_num):
                self.follow_tag_product_layout.addWidget(self.item_lists[i])
                self.follow_tag_product_layout.addSpacing(0)

            self.follow_tag_promotion_layout.addStretch(1)

            self.promo_layout = QVBoxLayout(self)
            self.promo_layout.setContentsMargins(0, 0, 0, 0)
            self.promo_layout.addSpacing(0)
            for i in range(self.promo_num_max):
                self.promo_layout.addWidget(self.promo_lists[i])
                self.promo_layout.addSpacing(0)

            self.promo_layout.addStretch(1)
            self.follow_main_layout.addLayout(self.follow_tag_product_layout, 2)
            self.follow_main_layout.addSpacing(1)
            self.follow_main_layout.addLayout(self.promo_layout, 1)

class FollowingTab(QScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("follow_tab")
        self.init_ui()
    def init_ui(self):
        def add_content_tabs():
            self.follow_tabs = follow_tabs = QTabWidget(self)
            follow_tabs.setObjectName("follow_tabs")
            follow_tabs.addTab(FollowingTagTab(self.follow_tabs), "Tag")
            follow_tabs.addTab(FollowingSellTab(self.follow_tabs), "Sell")
        add_content_tabs()

        def set_layout():
            self.follow_main_layout = follow_main_layout = QHBoxLayout()
            follow_main_layout.addWidget(self.follow_tabs)
            self.setLayout(self.follow_main_layout)
        set_layout()
        load_stylesheet(self, "follow.qss")
        print("Loading stylesheet of following tab widget")

class TableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):

        self.setMinimumWidth(self.parent.width())
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setHighlightSections(False)


    def set_right_menu(self, func):
        self.customContextMenuRequested[QPoint].connect(func)



class HorizontalLine(QFrame):
    def __init__(self, parent=None, wid=2):
        super().__init__(parent)
        self.parent = parent
        self.wid = wid
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(self.wid)

class Product(QScrollArea):
    def __init__(self, parent=None, item={}, mode=""):
        super().__init__(parent)
        self.parent = parent
        self.item = item
        self.mode = mode
        self.init_ui()

    def init_ui(self):

        self.path = osp.join(root_dir, "cpchain/assets/wallet/font", "ARLRDBD.TTF")
        self.font_regular = QFontDatabase.addApplicationFont(str(self.path))
        self.font_givenname = QFontDatabase.applicationFontFamilies(self.font_regular)[0]
        self.setFont(QFont(self.font_givenname))

        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumHeight(200)
        self.setMaximumHeight(500)
        self.setMinimumHeight(120)
        self.setMaximumHeight(120)
        self.title_btn = QPushButton("Medicine big data from Mayo Clinic")
        self.title_btn.setObjectName("title_btn")
        self.title_btn.clicked.connect(self.title_clicked_act)
        self.title_btn.setCursor(QCursor(Qt.PointingHandCursor))

        self.seller_btn = QPushButton("Barack Obama")
        self.seller_btn.setObjectName("seller_btn")
        self.seller_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.seller_btn.clicked.connect(self.seller_clicked_act)

        self.time_label = QLabel("May 4, 2018")
        self.time_label.setObjectName("time_label")
        self.total_sale_label = QLabel("128 sales")
        self.total_sale_label.setObjectName("total_sale_label")
        self.price_label = QLabel("$18")
        self.price_label.setObjectName("price_label")

        self.gap_line = HorizontalLine(self, 2)
        self.gap_line.setObjectName("gap_line")

        self.tag = ["tag1", "tag2", "tag3", "tag4"]
        self.tag_num = 4
        self.tag_btn_list = []

        for i in range(self.tag_num):
            self.tag_btn_list.append(QPushButton(self.tag[i], self))
            self.tag_btn_list[i].setObjectName("tag_btn_{0}".format(i))
            self.tag_btn_list[i].setProperty("t_value", 1)
            self.tag_btn_list[i].setCursor(QCursor(Qt.PointingHandCursor))
            self.tag_btn_list[i].clicked.connect(self.tag_clicked_act)

        def setlayout():
            self.main_layout = main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addSpacing(0)
            main_layout.addWidget(self.title_btn)
            main_layout.addSpacing(5)

            if self.mode != "simple":
                self.sales_layout = QHBoxLayout(self)
                self.sales_layout.setContentsMargins(0, 0, 0, 0)
                self.sales_layout.setSpacing(0)
                self.sales_layout.addWidget(self.total_sale_label)
                self.sales_layout.addStretch(1)
                self.sales_layout.addWidget(self.seller_btn)
                self.sales_layout.addSpacing(5)
                self.sales_layout.addWidget(self.time_label)
                self.sales_layout.addStretch(2)
                self.main_layout.addLayout(self.sales_layout)
                main_layout.addSpacing(10)
                self.main_layout.addWidget(self.price_label)

            self.tag_layout = QHBoxLayout(self)
            self.tag_layout.setContentsMargins(0, 5, 0, 5)
            self.tag_layout.addSpacing(1)
            for i in range(self.tag_num):
                self.tag_layout.addWidget(self.tag_btn_list[i])
                self.tag_layout.addSpacing(5)

            self.tag_layout.addStretch(1)
            self.main_layout.addLayout(self.tag_layout)
            self.main_layout.addSpacing(5)
            self.main_layout.addWidget(self.gap_line)
            self.main_layout.addSpacing(0)
            self.setLayout(self.main_layout)
        setlayout()
        load_stylesheet(self, "product.qss")

    @inlineCallbacks
    def get_product_info(self):
        product_info = self.item
        promo_list = yield wallet.market_client.query_promotion()
        main_wnd.findChild(QWidget, 'productdetail_tab').update_page(product_info, promo_list)

    def title_clicked_act(self):
        self.get_product_info()
        wid = main_wnd.content_tabs.findChild(QWidget, "productdetail_tab")
        main_wnd.content_tabs.setCurrentWidget(wid)

    def seller_clicked_act(self):
        wid = main_wnd.content_tabs.findChild(QWidget, "sellerHP_tab")
        main_wnd.content_tabs.setCurrentWidget(wid)

    def tag_clicked_act(self):
        wid = main_wnd.content_tabs.findChild(QWidget, "tagHP_tab")
        main_wnd.content_tabs.setCurrentWidget(wid)


class Product2(QScrollArea):
    tab_count = 0
    def __init__(self, parent=None, item={}, mode="", navi=""):
        super().__init__()
        self.parent = parent
        self.item = item
        self.mode = mode
        self.init_ui()
        self.navi = navi

    def init_ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumHeight(200)
        self.setMaximumHeight(500)
        self.setMinimumHeight(120)
        self.setMaximumHeight(120)
        self.title_btn = QPushButton(self.item['title'])
        self.title_btn.setObjectName("title_btn")
        self.title_btn.clicked.connect(self.title_clicked_act)
        self.title_btn.setCursor(QCursor(Qt.PointingHandCursor))

        self.seller_btn = QPushButton('barack obama')
        self.seller_btn.setObjectName("seller_btn")
        self.seller_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.seller_btn.clicked.connect(self.seller_clicked_act)

        self.time_label = QLabel(self.item['created'])
        self.time_label.setObjectName("time_label")
        self.total_sale_label = QLabel(str(self.item['sales_number']))
        self.total_sale_label.setObjectName("total_sale_label")
        self.price_label = QLabel('$'+str(self.item['price']))
        self.price_label.setObjectName("price_label")

        self.gap_line = HorizontalLine(self, 2)
        self.gap_line.setObjectName("gap_line")
        if isinstance(self.item['tags'], str):
            self.item['tags'] = self.item['tags'].split(',')
        self.tag = self.item['tags']
        self.tag_num = len(self.tag)
        self.tag_btn_list = []

        for i in range(self.tag_num):
            self.tag_btn_list.append(QPushButton(self.tag[i], self))
            self.tag_btn_list[i].setObjectName("tag_btn_{0}".format(i))
            self.tag_btn_list[i].setProperty("t_value", 1)
            self.tag_btn_list[i].setCursor(QCursor(Qt.PointingHandCursor))
            self.tag_btn_list[i].clicked.connect(self.tag_clicked_act)

        def setlayout():
            self.main_layout = main_layout = QVBoxLayout(self)
            main_layout.addSpacing(0)
            main_layout.addWidget(self.title_btn)
            main_layout.addSpacing(5)

            if self.mode != "simple":
                self.sales_layout = QHBoxLayout(self)
                self.sales_layout.addWidget(self.total_sale_label)
                self.sales_layout.addStretch(1)
                self.sales_layout.addWidget(self.seller_btn)
                self.sales_layout.addSpacing(5)
                self.sales_layout.addWidget(self.time_label)
                self.sales_layout.addStretch(2)
                self.main_layout.addLayout(self.sales_layout)
                main_layout.addSpacing(10)

            self.main_layout.addWidget(self.price_label)

            self.tag_layout = QHBoxLayout(self)
            self.tag_layout.addSpacing(1)
            for i in range(self.tag_num):
                self.tag_layout.addWidget(self.tag_btn_list[i])
                self.tag_layout.addSpacing(5)

            self.tag_layout.addStretch(1)
            self.main_layout.addLayout(self.tag_layout)
            self.main_layout.addSpacing(5)
            self.main_layout.addWidget(self.gap_line)
            self.main_layout.addSpacing(0)
            self.setLayout(self.main_layout)
        setlayout()
        load_stylesheet(self, "product.qss")
        logger.debug("Loading stylesheet of item")


    def title_clicked_act(self):

        Product2.tab_count = Product2.tab_count + 1
        content_tabs = main_wnd.content_tabs
        product_detail_tab = ProductDetailTab(content_tabs, self.item)
        tab_index = content_tabs.addTab(product_detail_tab, "")
        content_tabs.setCurrentIndex(tab_index)

    def seller_clicked_act(self):
        wid = main_wnd.content_tabs.findChild(QWidget, "sellerHP_tab")
        main_wnd.content_tabs.setCurrentWidget(wid)

    def tag_clicked_act(self):
        wid = main_wnd.content_tabs.findChild(QWidget, "tagHP_tab")
        main_wnd.content_tabs.setCurrentWidget(wid)


class PopularTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("popular_tab")

        self.init_ui()

    def init_ui(self):

        self.item_num_max = 2
        self.promo_num_max = 2

        self.item_lists = []
        self.promo_lists = []

        self.horline1 = HorizontalLine(self, 2)
        self.horline1.setObjectName("horline1")
        self.horline2 = HorizontalLine(self, 2)
        self.horline2.setObjectName("horline2")

        self.banner_label = QLabel(self)
        def create_banner(carousel):
            path = osp.join(root_dir, carousel[0]['image'])
            pixmap = QPixmap(path)  # get_pixm('cpc-logo-single.png')
            pixmap = pixmap.scaled(740, 195)
            self.banner_label.setPixmap(pixmap)

        d_banner = wallet.market_client.query_carousel()
        d_banner.addCallback(create_banner)

        self.hot_label = QLabel("Hot Industry")
        self.hot_label.setObjectName("hot_label")
        self.hot_label.setMinimumHeight(2)
        self.hot_label.setMaximumHeight(25)

        self.more_btn_1 = more_btn_1 = QPushButton("More>", self)
        more_btn_1.setObjectName("more_btn_1")
        self.more_btn_1.setCursor(QCursor(Qt.PointingHandCursor))
        self.more_btn_2 = more_btn_2 = QPushButton("More>", self)
        more_btn_2.setObjectName("more_btn_2")
        self.more_btn_2.setCursor(QCursor(Qt.PointingHandCursor))


        def create_hot_industry():
            self.hot_industry_label = []
            for i in range(config.wallet.hot_industry_num):
                hot_industry = QLabel(self)
                hot_industry.setObjectName('hot_industry_' + str(i))
                self.hot_industry_label.append(hot_industry)
        create_hot_industry()

        def set_hot_industry(hot_industry):
            for i in range(config.wallet.hot_industry_num):
                self.hot_industry_label[i].setText(hot_industry[i]['tag'])
                self.hot_industry_label[i].setFont(QFont("Arial", 13, QFont.Light))
                self.hot_industry_label[i].setAlignment(Qt.AlignCenter)
                path = osp.join(root_dir, hot_industry[i]['image'])
                self.hot_industry_label[i].setStyleSheet("border-image: url({0}); color: #fefefe".format(path))
        d_hot_industry = wallet.market_client.query_hot_tag()
        d_hot_industry.addCallback(set_hot_industry)

        self.recom_label = QLabel("Recommended")
        self.recom_label.setObjectName("recom_label")
        self.recom_label.setMaximumHeight(25)

        self.promo_label = QLabel(self)

        d_products = wallet.market_client.query_recommend_product()
        def get_items(products):
            for i in range(self.item_num_max):
                self.item_lists.append(Product2(parent=self, item=products[i]))
            d_promotion = wallet.market_client.query_promotion()
            def get_promotion(products):
                for i in range(self.promo_num_max):
                    self.promo_lists.append(Product2(parent=self, item=products[i], mode="simple"))
                set_layout()
            d_promotion.addCallback(get_promotion)
        d_products.addCallback(get_items)

        def set_layout():
            self.main_layout = QVBoxLayout(self)
            self.main_layout.setSpacing(0)
            self.main_layout.setContentsMargins(31, 20, 31, 10)

            self.banner_layout = QHBoxLayout(self)
            self.banner_layout.addWidget(self.banner_label)
            self.main_layout.addLayout(self.banner_layout)
            self.main_layout.addSpacing(35)
            self.main_layout.addWidget(self.hot_label)

            self.hot_layout = QHBoxLayout(self)
            self.hot_layout.addSpacing(0)
            self.hot_layout.addWidget(self.hot_label)
            self.hot_layout.addSpacing(50)
            self.hot_layout.addWidget(more_btn_1)
            self.main_layout.addLayout(self.hot_layout)
            self.main_layout.addSpacing(1)
            self.main_layout.addWidget(self.horline1)

            self.hot_img_layout = QHBoxLayout(self)
            for i in range(config.wallet.hot_industry_num):
                self.hot_img_layout.addSpacing(25)
                self.hot_img_layout.addWidget(self.hot_industry_label[i])
            self.main_layout.addLayout(self.hot_img_layout)
            self.main_layout.addSpacing(1)
            self.recom_layout = QHBoxLayout(self)
            self.recom_layout.addSpacing(0)
            self.recom_layout.addWidget(self.recom_label)
            self.recom_layout.addSpacing(50)
            self.recom_layout.addWidget(more_btn_2)
            self.main_layout.addLayout(self.recom_layout)
            self.main_layout.addSpacing(1)
            self.main_layout.addWidget(self.horline2)
            self.main_layout.addSpacing(1)
            self.bottom_layout = QHBoxLayout(self)
            self.bottom_layout.setContentsMargins(0, 0, 0, 0)

            self.product_layout = QVBoxLayout(self)
            self.product_layout.setContentsMargins(0, 0, 0, 0)
            for i in range(self.item_num_max):
                self.product_layout.addWidget(self.item_lists[i])
                self.product_layout.addSpacing(1)

            self.product_layout.addStretch(1)
            self.promo_layout = QVBoxLayout(self)
            self.promo_layout.setContentsMargins(0, 0, 0, 0)
            self.promo_layout.addSpacing(0)
            for i in range(self.promo_num_max):
                if i == len(self.promo_lists) - 1:
                    break
                self.promo_layout.addWidget(self.promo_lists[i])
                self.promo_layout.addSpacing(0)

            self.promo_layout.addStretch(1)
            self.bottom_layout.addLayout(self.product_layout, 2)
            self.bottom_layout.addLayout(self.promo_layout, 1)

            self.main_layout.addLayout(self.bottom_layout)
            load_stylesheet(self, "popular.qss")

    def handld_hotindustry_clicked(self):
        wid = main_wnd.content_tabs.findChild(QWidget, "tagHP_tab")
        main_wnd.content_tabs.setCurrentWidget(wid)


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
            if self.check_record_list[i] == True:
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
        def __init__(self, parent=None):
            super().__init__()
            self.parent = parent
            self.resize(500, 180)
            self.setWindowTitle("Publish your products")
            self.cloud_choice = {"ipfs": False, "s3": False}
            self.file_choice = ""
            self.init_ui()

        def init_ui(self):

            def create_btns():
                self.ipfs_btn = ipfs_btn = QRadioButton(self)
                ipfs_btn.setText("IPFS")
                ipfs_btn.setObjectName("ipfs_btn")
                ipfs_btn.setChecked(True)
                self.s3_btn = s3_btn = QRadioButton(self)
                s3_btn.setText("Amazon S3")
                s3_btn.setObjectName("s3_btn")
                self.file_choose_btn = file_choose_btn = QPushButton("Open File")
                file_choose_btn.setObjectName("file_choose_btn")

                self.cancel_btn = cancel_btn = QPushButton("Cancel")
                cancel_btn.setObjectName("cancel_btn")
                self.ok_btn = ok_btn = QPushButton("OK")
                ok_btn.setObjectName("ok_btn")
            create_btns()

            def create_labels():
                self.choice_label = choice_label = QLabel("Please select where you want to upload your data from one of the below two services: ")
                choice_label.setObjectName("choice_label")
                self.choice_label.setWordWrap(True)
            create_labels()

            def bind_slots():
                self.file_choose_btn.clicked.connect(self.choose_file)
                self.cancel_btn.clicked.connect(self.handle_cancel)
                self.ok_btn.clicked.connect(self.handle_ok)
            bind_slots()

            def set_layout():
                self.main_layout = main_layout = QVBoxLayout(self)
                main_layout.addSpacing(0)
                main_layout.addWidget(self.choice_label)
                main_layout.addSpacing(0)

                self.choosebtn_layout = choosebtn_layout = QHBoxLayout(self)
                choosebtn_layout.addStretch(1)
                choosebtn_layout.addWidget(self.ipfs_btn)
                choosebtn_layout.addSpacing(10)
                choosebtn_layout.addWidget(self.s3_btn)
                choosebtn_layout.addSpacing(10)
                choosebtn_layout.addWidget(self.file_choose_btn)
                choosebtn_layout.addStretch(1)

                main_layout.addLayout(self.choosebtn_layout)

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

            self.show()

        def choose_file(self):
            self.file_choice = QFileDialog.getOpenFileName()[0]

        def handle_cancel(self):
            self.file_choice = ""
            self.ipfs_btn.setChecked(True)
            self.s3_btn.setChecked(False)

            self.close()

        def handle_ok(self):
            if self.file_choice == "":
                QMessageBox.warning(self, "Warning", "Please select your files to upload first !")
                return
            else:
                if self.ipfs_btn.isChecked():
                    print("start uploading")
                    d_upload = fs.upload_file_ipfs(self.file_choice)
                    self.handle_ok_callback(d_upload)
                if self.s3_btn.isChecked():
                    print("upload to s3")
                    d_upload = deferToThread(fs.upload_file_s3, self.file_choice)
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

                    logger.debug("update table successfully !")
                    QMessageBox.information(self, "Tips", "Uploaded successfuly")
                else:
                    logger.debug('upload file info to market failed')
            d.addCallback(handle_upload_resp)


    def handle_upload(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
            return
        self.upload_dialog = CloudTab.UploadDialog(self)

    def handle_delete_act(self):
        self.file_table.removeRow(self.cur_clicked)

    def handle_publish_act(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
        else:
            product_id = self.file_table.item(self.cur_clicked, 5).text()
            self.publish_dialog = PublishDialog(self, product_id=product_id, tab='cloud')


class SideBar(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.content_tabs = parent.content_tabs
        self.init_ui()

    def init_ui(self):

        self.setObjectName("sidebar")
        self.setMaximumWidth(180)

        self.frame = QFrame()
        self.setWidget(self.frame)
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(150)

        def add_labels():
            self.trend_label = QLabel("Trending")
            self.trend_label.setObjectName("trend_label")
            self.trend_label.setMaximumHeight(25)

            self.mine_label = QLabel("Mine")
            self.mine_label.setObjectName("mine_label")
            self.trend_label.setMaximumHeight(25)

            self.treasure_label = QLabel("Treasure")
            self.treasure_label.setObjectName("treasure_label")
            self.treasure_label.setMaximumHeight(25)
        add_labels()

        def add_lists():
            self.trending_list = QListWidget()
            self.trending_list.setMaximumHeight(100)
            self.trending_list.addItem(QListWidgetItem(get_icon("pop.png"), "Popular"))
            self.trending_list.addItem(QListWidgetItem(get_icon("following.png"), "Following"))
            self.trending_list.setContentsMargins(0, 0, 0, 0)

            self.mine_list = QListWidget()
            self.mine_list.setMaximumHeight(100)
            self.mine_list.addItem(QListWidgetItem(get_icon("cloud.png"), "Cloud"))
            self.mine_list.addItem(QListWidgetItem(get_icon("store.png"), "Selling"))
            self.mine_list.setContentsMargins(0, 0, 0, 0)

            self.treasure_list = QListWidget()
            self.treasure_list.setMaximumHeight(100)
            self.treasure_list.addItem(QListWidgetItem(get_icon("purchased.png"), "Purchased"))
            self.treasure_list.addItem(QListWidgetItem(get_icon("collection.png"), "Collection"))
            self.treasure_list.addItem(QListWidgetItem(get_icon("collection.png"), "Shopping Cart"))
            self.treasure_list.setContentsMargins(0, 0, 0, 0)

            self.trending_list.setCurrentRow(0)
        add_lists()

        def bind_slots():
            def trending_list_clicked(item):
                item_to_tab_name = {
                    "Popular": "popular_tab",
                    "Following": "follow_tab",
                }
                wid = self.content_tabs.findChild(QWidget, item_to_tab_name[item.text()])
                self.content_tabs.setCurrentWidget(wid)
                self.mine_list.setCurrentRow(-1)
                self.treasure_list.setCurrentRow(-1)
            self.trending_list.itemPressed.connect(trending_list_clicked)

            def mine_list_clicked(item):
                item_to_tab_name = {
                    "Cloud": "cloud_tab",
                    "Selling": "selling_tab",
                }
                tab_index = main_wnd.main_tab_index[item_to_tab_name[item.text()]]
                main_wnd.content_tabs.setCurrentIndex(tab_index)

                self.trending_list.setCurrentRow(-1)
                self.treasure_list.setCurrentRow(-1)
            self.mine_list.itemPressed.connect(mine_list_clicked)

            def treasure_list_clicked(item):
                item_to_tab_name = {
                    "Purchased": "purchase_tab",
                    "Collection": "collect_tab",
                    "Shopping Cart": "collect_tab",
                }
                tab_index = main_wnd.main_tab_index[item_to_tab_name[item.text()]]
                main_wnd.content_tabs.setCurrentIndex(tab_index)
                self.trending_list.setCurrentRow(-1)
                self.mine_list.setCurrentRow(-1)
            self.treasure_list.itemPressed.connect(treasure_list_clicked)

        bind_slots()

        def set_layout():
            self.main_layout = main_layout = QVBoxLayout(self.frame)
            self.main_layout.setContentsMargins(0, 0, 0, 0)

            main_layout.addSpacing(10)
            main_layout.addWidget(self.trend_label)
            main_layout.addSpacing(3)
            main_layout.addWidget(self.trending_list)
            main_layout.addSpacing(1)
            main_layout.addWidget(self.mine_label)
            main_layout.addSpacing(3)
            main_layout.addWidget(self.mine_list)
            main_layout.addSpacing(1)
            main_layout.addWidget(self.treasure_label)
            main_layout.addSpacing(3)
            main_layout.addWidget(self.treasure_list)
            main_layout.addStretch(1)
            self.setLayout(self.main_layout)
        set_layout()
        load_stylesheet(self, "sidebar.qss")


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
            self.word_label = word_label = QLabel(self)
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
            QMessageBox.information(main_wnd, "Tips", "Please login first !")
            return
        wid = main_wnd.content_tabs.findChild(QWidget, "cloud_tab")
        self.upload_dlg = CloudTab.UploadDialog(wid)
        self.upload_dlg.show()



class MainWindow(QMainWindow):
    def __init__(self, reactor):
        super().__init__()
        self.reactor = reactor
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle('CPChain Wallet')
        self.setObjectName("main_window")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.main_tab_index = {}

        def set_geometry():
            self.resize(1002, 710)  # resize before centering.
            self.setMinimumSize(800, 500)
            center_pt = QDesktopWidget().availableGeometry().center()
            qrect = self.frameGeometry()
            qrect.moveCenter(center_pt)
            self.move(qrect.topLeft())
        set_geometry()

        def add_content_tabs():
            self.content_tabs = content_tabs = QTabWidget(self)
            content_tabs.setObjectName("content_tabs")
            content_tabs.tabBar().hide()
            content_tabs.setContentsMargins(0, 0, 0, 0)
            self.pop_index = content_tabs.addTab(PopularTab(content_tabs), "")
            self.cloud_index = content_tabs.addTab(CloudTab(content_tabs), "")
            self.follow_index = content_tabs.addTab(FollowingTab(content_tabs), "")
            self.sell_index = content_tabs.addTab(SellTab(content_tabs), "")
            content_tabs.addTab(PersonalProfileTab(content_tabs), "")
            content_tabs.addTab(TagHPTab(content_tabs), "")
            content_tabs.addTab(SellerHPTab(content_tabs), "")
            content_tabs.addTab(SecurityTab(content_tabs), "")
            content_tabs.addTab(PreferenceTab(content_tabs), "")
            content_tabs.addTab(PersonalInfoPage(content_tabs), "")
            self.purchase_index = content_tabs.addTab(PurchasedTab(content_tabs), "")
            self.collect_index = content_tabs.addTab(CollectedTab(content_tabs), "")
            self.main_tab_index = {
                "cloud_tab": self.cloud_index,
                "selling_tab": self.sell_index,
                "purchase_tab": self.purchase_index,
                "collect_tab": self.collect_index
            }
        add_content_tabs()

        self.header = Header(self)
        self.sidebar = SideBar(self)


        def set_layout():
            self.main_layout = main_layout = QVBoxLayout()
            self.main_layout.setSpacing(0)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addSpacing(0)
            main_layout.addWidget(self.header)

            self.content_layout = content_layout = QHBoxLayout()
            self.content_layout.setSpacing(0)
            self.content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.addSpacing(0)
            content_layout.addWidget(self.sidebar)
            content_layout.addSpacing(0)
            content_layout.addWidget(self.content_tabs)

            self.main_layout.addLayout(self.content_layout)

            wid = QWidget(self)
            wid.setLayout(self.main_layout)
            self.setCentralWidget(wid)
        set_layout()
        load_stylesheet(self, "main_window.qss")

        self.show()

    def update_purchased_tab(self, nex_tab='downloaded'):

        tab_index = self.main_tab_index['purchase_tab']
        self.content_tabs.removeTab(tab_index)
        for key in self.main_tab_index:
            if self.main_tab_index[key] > tab_index:
                self.main_tab_index[key] -= 1
        tab_index = self.content_tabs.addTab(PurchasedTab(main_wnd.content_tabs), "")
        self.main_tab_index['cloud_tab'] = tab_index
        self.content_tabs.setCurrentIndex(tab_index)
        wid = self.content_tabs.currentWidget()
        if nex_tab == 'downloading':
            wid.purchased_main_tab.setCurrentIndex(1)
        elif nex_tab == 'downloaded':
            wid.purchased_main_tab.setCurrentIndex(0)
        else:
            logger.debug("Wrong parameter!")

    def closeEvent(self, event):
        self.reactor.stop()

def _handle_keyboard_interrupt():
    def sigint_handler(*args):
        QApplication.quit()

    import signal
    signal.signal(signal.SIGINT, sigint_handler)

    from PyQt5.QtCore import QTimer

    _handle_keyboard_interrupt.timer = QTimer()
    timer = _handle_keyboard_interrupt.timer
    timer.start(300)
    timer.timeout.connect(lambda: None)

def initialize_system():
    def monitor_chain_event():
        monitor_new_order = LoopingCall(wallet.chain_broker.monitor.monitor_new_order)
        monitor_new_order.start(10)

        handle_new_order = LoopingCall(wallet.chain_broker.handler.handle_new_order)
        handle_new_order.start(15)

        monitor_ready_order = LoopingCall(wallet.chain_broker.monitor.monitor_ready_order)
        monitor_ready_order.start(20)

        handle_ready_order = LoopingCall(wallet.chain_broker.handler.handle_ready_order)
        handle_ready_order.start(25)

        monitor_confirmed_order = LoopingCall(wallet.chain_broker.monitor.monitor_confirmed_order)
        monitor_confirmed_order.start(30)
    monitor_chain_event()


def main():
    global main_wnd
    main_wnd = MainWindow(reactor)
    _handle_keyboard_interrupt()

    initialize_system()
    wallet.set_main_wnd(main_wnd)

    sys.exit(reactor.run())


if __name__ == '__main__':
    main()
