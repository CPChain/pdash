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
        # if wallet.market_client.token == '':
        #     QMessageBox.information(self, "Tips", "Please login first !")
        #     return
        upload = UploadDialog(self)
        upload.show()
        # self.dig = MyDataTab.StorageSelectionDlg(self)

    def handle_delete_act(self):
        self.file_table.removeRow(self.cur_clicked)

    def handle_publish_act(self):
        if wallet.market_client.token == '':
            QMessageBox.information(self, "Tips", "Please login first !")
        else:
            product_id = self.file_table.item(self.cur_clicked, 5).text()
            self.publish_dialog = PublishDialog(self, product_id=product_id, tab='cloud')

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
                    tab_index = main_wnd.content_tabs.addTab(MyDataTab(main_wnd.content_tabs), "")
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
            self.upload_dlg = MyDataTab.UploadDialog(storage_service)
            self.close()
            self.upload_dlg.show()

        def handle_cancel(self):
            self.close()
