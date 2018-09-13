from PyQt5.QtCore import Qt, QPoint, QObjectCleanupHandler
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout, QWidget, QDialog, QFrame, QTableWidgetItem,
                             QAbstractItemView, QMessageBox, QTextEdit, QHeaderView, QTableWidget, QRadioButton,
                             QFileDialog, QListWidget, QListWidgetItem, QComboBox)
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
import re
import traceback

from cpchain import root_dir

from cpchain.wallet.pages import main_wnd, HorizontalLine, abs_path, get_icon, Binder, warning
from cpchain.wallet.components.loading import Loading

class FileUpload(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        ###初始化打开接受拖拽使能
        self.setAcceptDrops(True)
        self.initUI()

    def onOpen(self, event):
        file_choice = QFileDialog.getOpenFileName()[0]
        self.target.setText(file_choice)

    @property
    def file(self):
        return self.target.text()

    def initUI(self):
        layout = QGridLayout(self)
        hint = QLabel('Drop file here or')
        layout.addWidget(QLabel(""), 0, 0)

        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignLeft)
        hbox.addWidget(hint)
        self.open_text = QLabel('open...')
        self.open_text.setObjectName('open')
        Binder.click(self.open_text, self.onOpen)

        hbox.addWidget(self.open_text)
        hbox.addStretch(1)

        layout.addLayout(hbox, 1, 0, 2, 1)
        self.target = QLabel("")
        layout.addWidget(self.target, 3, 0)
        layout.addWidget(QLabel(""), 4, 0)
        self.setLayout(layout)
        self.setStyleSheet("""
            QFrame {
                background: white;
            }
            #open {
                color:#4a90e2;
                height: 20px;
            }
        """)

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        st = str(event.mimeData().urls())
        st = re.compile(r'\'file:\/\/(.*?)\'').findall(st)[0]
        self.target.setText(st)

class UploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 180)
        self.setWindowTitle("Upload your file")
        self.storage_index = 0
        self.now_wid = None
        
        self.storage = [
            {
                'name': 'Amazon S3',
                'type': 's3',
                'options': [
                    {
                        'type': 'edit',
                        'name': 'Bucket',
                        'id': 'bucket'
                    }, {
                        'type': 'edit',
                        'name': 'aws_secret_access_key',
                        'id': 'aws_secret_access_key'
                    }, {
                        'type': 'edit',
                        'name': 'aws_access_key_id',
                        'id': 'aws_access_key_id'
                    }, {
                        'type': 'edit',
                        'name': 'Key',
                        'id': 'key'
                    }
                ],
                'listener': None
            }, {
                'name': 'IPFS',
                'type': 'ipfs',
                'options': [
                    {
                        'type': 'edit',
                        'name': 'Host',
                        'id': 'host'
                    }, {
                        'type': 'edit',
                        'name': 'Port',
                        'id': 'port'
                    }
                ],
                'listener': None
            }, {
                # 'name': 'Proxy',
                # 'options': [
                #     {
                #         'type': 'combo',
                #         'items': ['1', '2', '3']
                #     }
                # ]
            }
        ]
        self.max_row = 0
        for i in self.storage:
            if i:
                self.max_row = max(self.max_row, len(i['options']))
        self.initUI()

    def onChangeStorage(self, index):
        self.storage_index = index
        new_wid = self.build_option_widget(self.storage[self.storage_index])
        self.layout.replaceWidget(self.now_wid, new_wid)
        self.now_wid.deleteLater()
        del self.now_wid
        self.now_wid = new_wid

    def build_option_widget(self, storage):
        if not storage:
            return
        storage_module = importlib.import_module(
            "cpchain.storage-plugin." + storage['type']
        )
        self.dst = storage_module.Storage().user_input_param()

        grid = QGridLayout()
        grid.setObjectName('grid')
        grid.setContentsMargins(0, 0, 0, 0)
        row = 0
        options = storage['options']
        for option in options:
            if option['type'] == 'edit':
                grid.addWidget(QLabel(option['name'] + ":"), row, 1)
                wid = QLineEdit()
                wid.setObjectName(f'{storage["type"]}-{option["id"]}')
                wid.setText(self.dst[option['id']])
                grid.addWidget(wid, row, 3)
            elif option['type'] == 'combo':
                items = QComboBox()
                for item in option['items']:
                    items.addItem(item)
                grid.addWidget(items, row, 3)
            row += 1
        for i in range(self.max_row - len(options)):
            grid.addWidget(QLabel(""), row, 3)
            row += 1
        wid = QWidget()
        wid.setLayout(grid)
        wid.setContentsMargins(0, 0, 0, 0)
        wid.setStyleSheet("""
            QWidget {
                
            }
            QComboBox {
                
            }
        """)
        return wid

    def initUI(self):
        layout = QGridLayout(self)
        layout.setSpacing(20)
        # Data name
        data_name = QLineEdit()
        layout.addWidget(QLabel('Data Name:'), 0, 1)
        layout.addWidget(data_name, 0, 2, 1, 2)

        # Storage location
        layout.addWidget(QLabel('Storage location:'), 1, 1)
        storage = QComboBox()
        for item in self.storage:
            if item:
                storage.addItem(item['name'])
        storage.currentIndexChanged.connect(self.onChangeStorage)
        layout.addWidget(storage, 1, 2, 1, 2)

        # Storage Options
        layout.addWidget(QLabel(""), 2, 1, self.max_row, 1)

        self.now_wid = self.build_option_widget(self.storage[self.storage_index])
        layout.addWidget(self.now_wid, 2, 2, self.max_row, 2)

        # File Drop or Open
        fileSlt = FileUpload()
        fileSlt.setMinimumHeight(120)
        fileSlt.setMaximumHeight(120)
        layout.addWidget(fileSlt, self.max_row + 2, 1, 3, 3)

        # Ok and Cancel
        bottom = QHBoxLayout()
        bottom.setAlignment(Qt.AlignRight)
        bottom.setSpacing(10)
        bottom.addStretch(1)

        cancel = QLabel('Cancel')
        def closeListener(event):
            self.close()
        Binder.click(cancel, closeListener)
        bottom.addWidget(cancel)

        ok = QPushButton('OK')

        def okListener(event):
            # Find All needed values
            storage = self.storage[self.storage_index]
            dst = dict()
            for option in storage['options']:
                objName = storage['type'] + '-' + option['id']
                child = self.findChild((QLineEdit,), objName)
                dst[option['id']] = child.text()
                if not dst[option['id']]:
                    warning(self)
                    return
            # Data Name
            dataname = data_name.text()
            if not dataname:
                warning(self, "Please input data name first")
                return
            # File
            file = fileSlt.file
            if not file:
                warning(self, "Please drag a file or open a file first")
                return
            d_upload = deferToThread(fs.upload_file, file, storage['type'], dst)
            d_upload.addCallback(self.handle_ok_callback)
            self.hide()
            self.loading = Loading()
            self.loading.show()
        ok.clicked.connect(okListener)
        bottom.addWidget(ok)

        layout.addWidget(QLabel(""), 4, 1)
        layout.addLayout(bottom, 5 + self.max_row, 2)
        self.setLayout(layout)
        self.layout = layout
    
    def handle_ok_callback(self, file_id):
        file_info = fs.get_file_by_id(file_id)
        hashcode = file_info.hashcode
        path = file_info.path
        size = file_info.size
        product_id = file_info.id
        remote_type = file_info.remote_type
        remote_uri = file_info.remote_uri
        name = file_info.name
        encrypted_key = RSACipher.encrypt(file_info.aes_key)
        encrypted_key = Encoder.bytes_to_base64_str(encrypted_key)
        d = wallet.market_client.upload_file_info(hashcode, path, size, product_id, remote_type, remote_uri, name, encrypted_key)
        def handle_upload_resp(status):
            self.loading.close()
            self.show()
            try:
                if status == 1:
                    QMessageBox.information(self, "Tips", "Uploaded successfuly")
                    self.close()
                else:
                    QMessageBox.information(self, "Tips", "Uploaded fail")
                    self.close()
            except Exception as e:
                traceback.print_exc()
                QMessageBox.information(self, "Tips", "Uploaded fail")
                self.close()
        d.addCallback(handle_upload_resp)
