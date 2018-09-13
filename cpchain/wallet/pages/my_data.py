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

from cpchain import root_dir

from cpchain.wallet.pages import main_wnd, HorizontalLine, abs_path, get_icon
from cpchain.wallet.pages.other import PublishDialog

from cpchain.wallet.components.table import Table
from cpchain.wallet.components.product import Product
from cpchain.wallet.components.product_list import ProductList
from cpchain.wallet.components.upload import UploadDialog
from cpchain.wallet.components.loading import Loading

logger = logging.getLogger(__name__)

class MyDataTab(QScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("my_data_tab")

        self.init_ui()

    def update_table(self):
        tab_index = main_wnd.main_tab_index[self.objectName]
        main_wnd.content_tabs.removeTab(tab_index)
        tab_index = main_wnd.content_tabs.addTab(MyDataTab(main_wnd.content_tabs), "")
        main_wnd.main_tab_index[self.objectName] = tab_index
        main_wnd.content_tabs.setCurrentIndex(tab_index)

    def init_ui(self):
        self.cur_clicked = 0
        btn_group = [
            {
                'id': 'upload_btn',
                'name': 'Upload Batch Data',
                'listener': self.onClickUpload
            }
        ]
        def buildBtnLayout(btn_group):
            btn_layout = QHBoxLayout(self)
            btn_layout.setAlignment(Qt.AlignLeft)
            for item in btn_group:
                btn = QPushButton(item['name'])
                btn.setObjectName(item['id'])
                btn.setMaximumWidth(200)
                btn.clicked.connect(item['listener'])
                btn_layout.addWidget(btn)
                btn_layout.addSpacing(5)
            return btn_layout

        header = {
            'headers': ['Name', 'Location', 'Size', 'Status'],
            'width': [252, 140, 140, 138]
        }
        data = fs.get_file_list()
        def itemHandler(data):
            items = []
            items.append(data.name)
            items.append(data.remote_type)
            items.append(sizeof_fmt(data.size))
            status = data.is_published
            wid = QLabel('Published')
            if not status:
                wid.setText('Publish as product')
                wid.setStyleSheet("QLabel{color: #006bcf;}")
            items.append(wid)
            return items

        table = Table(self, header, data, itemHandler, sort=2)
        table.setObjectName('my_table')
        table.setFixedWidth(700)
        table.setFixedHeight(180)
        # table.setMaximumHeight()

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)

        # Button Group
        main_layout.addLayout(buildBtnLayout(btn_group))
        main_layout.addSpacing(2)

        # Line
        main_layout.addWidget(HorizontalLine(self, 2))

        # My Product
        my_product_label = QLabel('My Product')
        my_product_label.setObjectName('label_hint')
        main_layout.addWidget(my_product_label)

        # Product List
        test_dict = dict(image=abs_path('icons/test.png'), icon=abs_path('icons/icon_batch@2x.png'), name="Name of a some published data name of a data")
        products = []
        for i in range(3):
            products.append(Product(**test_dict))

        pdsWidget = ProductList(products)
        main_layout.addWidget(pdsWidget)

        # Batch Data
        batch_label = QLabel('Batch Data')
        batch_label.setObjectName('label_hint')
        main_layout.addWidget(batch_label)

        main_layout.addWidget(table)
        main_layout.addStretch(1)

        widget = QWidget()
        widget.setObjectName('parent_widget')
        widget.setLayout(main_layout)
        widget.setFixedWidth(750)
        widget.setStyleSheet("QWidget#parent_widget{background: white;}")

        # Scroll Area Properties
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(False)
        scroll.setWidget(widget)

        vLayout = QVBoxLayout(self)
        vLayout.addWidget(scroll)
        self.setLayout(vLayout)
        load_stylesheet(self, "my_data.qss")

    def onClickUpload(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
            return
        upload = UploadDialog(self)
        upload.show()

    def handle_delete_act(self):
        self.file_table.removeRow(self.cur_clicked)

    def handle_publish_act(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
        else:
            product_id = self.file_table.item(self.cur_clicked, 5).text()
            self.publish_dialog = PublishDialog(self, product_id=product_id, tab='cloud')
