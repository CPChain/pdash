import os.path as osp
import hashlib
import logging

from PyQt5.QtWidgets import (QFrame, QDesktopWidget, QPushButton, QHBoxLayout, QMessageBox, QVBoxLayout, QGridLayout, QScrollArea, QListWidget, QListWidgetItem, QTabWidget, QLabel, QWidget, QLineEdit, QTableWidget, QTextEdit, QAbstractItemView, QTableWidgetItem, QHeaderView, QFileDialog, QDialog, QRadioButton, QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCursor, QPixmap, QFont

from cpchain import config, root_dir
from cpchain.wallet import fs


from cpchain.wallet.pages import load_stylesheet, HorizontalLine, wallet, main_wnd

logger = logging.getLogger(__name__)



# widgets

from cpchain.wallet.pages.personal import *
from cpchain.wallet.pages.product import *
from cpchain.wallet.pages.header import *
from cpchain.wallet.pages.purchase import *
from cpchain.wallet.pages.sidebar import *

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
        load_stylesheet(self, "publishdialog.qss")
        self.show()

    def handle_publish(self):
        self.pinfo_title = self.pinfo_title_edit.text()
        self.pinfo_type = 'file'
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
            d_publish = wallet.market_client.publish_product(self.product_id, self.pinfo_title, self.pinfo_type,
                                                             self.pinfo_descrip, self.pinfo_price,
                                                             self.pinfo_tag, self.start_date,
                                                             self.end_date)
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
