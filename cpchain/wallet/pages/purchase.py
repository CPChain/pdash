from PyQt5.QtCore import Qt, QPoint, QBasicTimer
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget, QProgressBar)
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

from cpchain.wallet.pages.product import TableWidget, PurchasedDownloadedTab

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
        return self.step >= self.max_step


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
