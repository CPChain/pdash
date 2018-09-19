from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget)
from PyQt5.QtGui import QCursor, QFont, QFontDatabase

from cpchain.wallet.pages import load_stylesheet, HorizontalLine, wallet, main_wnd, get_pixm

from twisted.internet.defer import inlineCallbacks
from cpchain.wallet import fs
from cpchain.utils import open_file, sizeof_fmt
from cpchain.proxy.client import pick_proxy

import os.path as osp
import string
import logging

from cpchain import config, root_dir
from cpchain.wallet.pages.personal import Seller

logger = logging.getLogger(__name__)

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

        self.size_label = QLabel("type: {}".format(self.product_info["ptype"]))
        self.size_label.setObjectName("type_label")

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
