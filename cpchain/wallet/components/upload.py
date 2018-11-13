import importlib
import logging
import os
import os.path as osp
import platform
import re
import string
import time
import traceback

from PyQt5.QtCore import (QObject, QObjectCleanupHandler, QPoint, Qt, QUrl,
                          pyqtProperty, pyqtSignal)
from PyQt5.QtGui import QCursor, QFont, QFontDatabase
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QCheckBox, QComboBox,
                             QDialog, QFileDialog, QFrame, QGridLayout,
                             QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QMenu, QMessageBox,
                             QPushButton, QRadioButton, QScrollArea,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QTextEdit, QVBoxLayout, QWidget)
from twisted.internet import reactor
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.threads import deferToThread

from cpchain import root_dir
from cpchain.crypto import ECCipher, Encoder, RSACipher
from cpchain.proxy.client import pick_proxy
from cpchain.utils import open_file, sizeof_fmt
from cpchain.wallet import fs
from cpchain.wallet.components.dialog import Dialog
from cpchain.wallet.components.gif import LoadingGif
from cpchain.wallet.pages import (Binder, HorizontalLine, abs_path, app,
                                  get_icon, get_pixm, load_stylesheet,
                                  main_wnd, qml_path, wallet, warning)
from cpchain.wallet.simpleqt import Component
from cpchain.wallet.simpleqt.decorator import component
from cpchain.wallet.simpleqt.model import ListModel
from cpchain.wallet.simpleqt.widgets import ComboBox, Input
from cpchain.wallet.simpleqt.widgets.label import Label

logger = logging.getLogger(__name__)

class FileUploadObject(QObject):

    def __init__(self, parent, width, height, background, text, browse_text, gap=3):
        self._width = width
        self._height = height
        self._background = background
        self._icon = '../../icons/add@2x.jpg'
        self._text = text
        self._browse_text = browse_text
        self._file = ""
        self._gap = gap
        return super().__init__(parent)

    @pyqtProperty(float)
    def width(self):
        return self._width

    @pyqtProperty(float)
    def height(self):
        return self._height

    @pyqtProperty(float)
    def gap(self):
        return self._gap

    @pyqtProperty(str)
    def background(self):
        return self._background

    @pyqtProperty(str)
    def icon(self):
        return self._icon

    @pyqtProperty(str)
    def text(self):
        return self._text

    @pyqtProperty(str)
    def browse_text(self):
        return self._browse_text

    @pyqtProperty(str)
    def file(self):
        return self._file

    @file.setter
    def file(self, _file):
        self._file = _file


class FileUploadQml(Component):
    qml = qml_path('components/FileUpload.qml')

    def __init__(self, parent=None, width=None, height=None,
                 text="Drop file here or",
                 browse_text="browse",
                 background="#fafafa",
                 gap=3):
        self.obj = FileUploadObject(None, width, height,
                                    background, text,
                                    browse_text,
                                    gap)
        return super().__init__(parent)

    @property
    def file(self):
        return self.obj.file

    @component.ui
    def ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        widget = QQuickWidget(self)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.rootContext().setContextProperty('self', self.obj)
        widget.setSource(QUrl(self.qml))
        layout.addWidget(widget)
        return layout


class FileUpload(QFrame):

    def __init__(self, parent=None, width=None, height=None, text="Drop file here or", browse_text="browse"):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.text = text
        self.browse_text = browse_text
        if self.width:
            self.setMinimumWidth(width)
            self.setMaximumWidth(width)
        if self.height:
            self.setMinimumHeight(height)
            self.setMaximumHeight(height)
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
        hint = QLabel(self.text)
        layout.addWidget(QLabel(""), 0, 0)

        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignLeft)
        hbox.addWidget(hint)
        self.open_text = QLabel(self.browse_text)
        self.open_text.setObjectName('open')
        Binder.click(self.open_text, self.onOpen)

        hbox.addWidget(self.open_text)
        hbox.addStretch(1)

        layout.addLayout(hbox, 1, 0, 2, 1)
        self.target = QLabel("")
        layout.addWidget(self.target, 3, 0)
        layout.addWidget(QLabel(""), 4, 0)
        self.setLayout(layout)
        self.setObjectName('main')
        self.setStyleSheet("""
            QFrame#main {
                background: white;
                border: 1px dashed #bbb;
                border-radius: 3px;
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
        sysstr = platform.system()
        if sysstr == "Windows":
            st = st[1:]
        self.target.setText(st)

class UploadDialog(Dialog):

    okSignal = pyqtSignal(int)

    def __init__(self, parent=None, oklistener=None):
        self.width_ = 550
        self.height_ = 630
        title = "Upload your file"
        self.storage_index = 0
        self.now_wid = None
        self.oklistener = oklistener

        self.storage = [
            {
                'name': 'Proxy',
                'type': 'proxy',
                'height': self.height_ - 200,
                'options': [
                    {
                        'type': 'combo',
                        'items': []
                    }
                ]
            },
            {
                'name': 'Amazon S3',
                'type': 's3',
                'options': [
                    {
                        'type': 'edit',
                        'name': 'Bucket',
                        'id': 'bucket'
                    },
                    {
                        'type': 'edit',
                        'name': 'aws_secret_access_key',
                        'id': 'aws_secret_access_key'
                    },
                    {
                        'type': 'edit',
                        'name': 'aws_access_key_id',
                        'id': 'aws_access_key_id'
                    },
                    {
                        'type': 'edit',
                        'name': 'Key',
                        'id': 'key'
                    }
                ],
                'listener': None
            }, {
                'name': 'IPFS',
                'type': 'ipfs',
                'height': self.height_ - 100,
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
            }
        ]
        self.proxy = ListModel([])
        self.create()
        self.max_row = 0
        for i in self.storage:
            if i:
                self.max_row = max(self.max_row, len(i['options']))
        self.data()
        super().__init__(wallet.main_wnd, title=title, width=self.width_, height=self.height_)
        self.okSignal.connect(self.handle_upload_resp)

    def onChangeStorage(self, index):
        self.storage_index = index
        new_wid = self.build_option_widget(self.storage[self.storage_index])
        height = self.storage[self.storage_index].get('height', self.height_)
        self.setHeight(height)
        self.main.replaceWidget(self.now_wid, new_wid)
        self.now_wid.deleteLater()
        del self.now_wid
        self.now_wid = new_wid


    def build_option_widget(self, storage):
        if not storage:
            return
        storage_module = importlib.import_module(
            "cpchain.storage_plugin." + storage['type']
        )
        self.dst = app.storage[storage['type']]

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        row = 0
        options = storage['options']
        for option in options:
            if option['type'] == 'edit':
                wid = QLineEdit()
                wid.setObjectName('{}-{}'.format(storage["type"], option["id"]))
                wid.setText(self.dst[option['id']])
                layout.addWidget(self.gen_row(option['name'] + ":", wid))
            if option['type'] == 'combo':
                wid = ComboBox(self.proxy)
                wid.setMinimumWidth(340)
                layout.addWidget(self.gen_row("Proxy:", wid))

            row += 1
        wid = QWidget()
        wid.setLayout(layout)
        wid.setContentsMargins(0, 0, 0, 0)
        wid.setStyleSheet("""
            QWidget {
                
            }
            QComboBox {
                
            }
        """)
        return wid

    def gen_row(self, name, widget, width=None):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        nameWid = QLabel(name)
        nameWid.setMinimumWidth(160)
        nameWid.setObjectName("name")
        layout.addWidget(nameWid)
        layout.addWidget(widget)
        if width:
            widget.setMinimumWidth(width)
        if isinstance(widget, Label):
            unit = Label('CPC')
            unit.setObjectName('unit')
            widget.setObjectName('value')
            layout.addWidget(unit)
        tmp = QWidget()
        tmp.setLayout(layout)
        tmp.setObjectName('item')
        return tmp

    @component.data
    def data(self):
        return {
            "data_name": ""
        }

    @component.create
    def create(self):
        def set_proxy(proxy):
            if proxy:
                self.proxy.value = list(set(proxy))
        pick_proxy().addCallbacks(set_proxy)

    def ui(self, widget):
        layout = QVBoxLayout(widget)
        layout.setSpacing(1)
        self.input_name = Input(self.data_name)
        layout.addWidget(self.gen_row('Data Name:', self.input_name))

        # Storage
        storage = QComboBox()
        for item in self.storage:
            if item:
                storage.addItem(item['name'])
        storage.currentIndexChanged.connect(self.onChangeStorage)
        layout.addWidget(self.gen_row('Storage Location:', storage))

        self.now_wid = self.build_option_widget(self.storage[self.storage_index])
        height = self.storage[self.storage_index].get('height', self.height_)
        self.setHeight(height)
        layout.addWidget(self.now_wid)

        print(self.input_name.width())
        # # File Drop or Open
        fileSlt = FileUploadQml(width=330, height=121, gap=1)
        layout.addWidget(self.gen_row("File:", fileSlt))
        self.fileSlt = fileSlt

        layout.addStretch(1)

        # Ok and Cancel
        bottom = QHBoxLayout()
        bottom.setAlignment(Qt.AlignRight)
        bottom.setSpacing(20)
        bottom.addStretch(1)

        self.cancel = QPushButton('Cancel')
        self.cancel.setObjectName('pinfo_cancel_btn')
        self.cancel.clicked.connect(lambda _: self.close())
        bottom.addWidget(self.cancel)

        ok = QPushButton('OK')
        ok.setObjectName('pinfo_publish_btn')
        ok.clicked.connect(self.okListener)
        bottom.addWidget(ok)

        self.loading = LoadingGif()
        self.ok = ok
        self.loading.hide()
        bottom.addWidget(self.loading)
        layout.addLayout(bottom)
        return layout

    def show_loading(self, flag):
        if flag:
            self.loading.show()
            self.ok.hide()
        else:
            self.loading.hide()
            self.ok.show()

    def okListener(self, _):
        self.show_loading(True)
        # Find All needed values
        storage = self.storage[self.storage_index]
        dst = dict()
        if storage['type'] == 'proxy':
            dst['proxy_id'] = self.proxy.current
        for option in storage['options']:
            if option['type'] == 'edit':
                objName = storage['type'] + '-' + option['id']
                child = self.findChild((QLineEdit,), objName)
                dst[option['id']] = child.text()
                if not dst[option['id']]:
                    warning(self)
                    self.show_loading(False)
                    return
        # save storage params
        deferToThread(app.save_params, storage['type'], dst)
        # Data Name
        dataname = self.data_name.value or self.input_name.text()
        if not dataname:
            warning(self, "Please input data name first")
            self.show_loading(False)
            return
        # File
        file = self.fileSlt.file
        if not file:
            warning(self, "Please drag a file or open a file first")
            self.show_loading(False)
            return
        fs.upload_file(file, storage['type'], dst, dataname).addCallbacks(self.handle_ok_callback)

    def handle_upload_resp(self, status):
        self.show_loading(False)
        try:
            if status == 1:
                app.msgbox.info("Uploaded successfuly")
                if self.oklistener:
                    self.oklistener()
                self.close()
            else:
                app.msgbox.error("Uploaded fail")
                self.close()
        except Exception as e:
            logger.error(e)
            app.msgbox.error("Uploaded fail")
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
        encrypted_key = RSACipher.encrypt(file_info.aes_key)
        encrypted_key = Encoder.bytes_to_base64_str(encrypted_key)
        d = wallet.market_client.upload_file_info(hashcode, path, size, product_id, remote_type, remote_uri, name, encrypted_key)
        def cb(status):
            self.okSignal.emit(status)
        d.addCallbacks(cb)

    def style(self):
        return super().style() + """
        QLabel {
            font-size:14px;
            color:#000000;
            text-align:left;
        }
        QLineEdit, QComboBox {
            font-size:13px;        
        }
        QLineEdit {
            border: 1px solid #ccc;
            border-radius: 4px;
            padding-top: 6px;
            padding-bottom: 6px;
            padding-left: 3px;
            background: white;
        }
        QPushButton#pinfo_cancel_btn{
            padding-left: 10px;
            padding-right: 10px;
            border: 1px solid #3173d8; 
            border-radius: 3px;
            color: #3173d8;
            min-height: 30px;
            max-height: 30px;
            background: #ffffff;
            min-width: 80px;
            max-width: 80px;
        }

        QPushButton#pinfo_cancel_btn:hover{
            border: 1px solid #3984f7; 
            color: #3984f6;
        }

        QPushButton#pinfo_cancel_btn:pressed{
            border: 1px solid #2e6dcd; 
            color: #2e6dcd;
            background: #e5ecf4;
        }

        QPushButton#pinfo_cancel_btn:disabled{
            border: 1px solid #8cb8ea; 
            color: #8cb8ea;
        }

        QPushButton#pinfo_publish_btn{
            padding-left: 10px;
            padding-right: 10px;
            border: 1px solid #3173d8; 
            border-radius: 3px;
            color: #ffffff;
            min-height: 30px;
            max-height: 30px;
            min-width: 80px;
            max-width: 80px;
            background: #3173d8;
        }

        QPushButton#pinfo_publish_btn:hover{
            background: #3984f7; 
            border: 1px solid #3984f7;
        }

        QPushButton#pinfo_publish_btn:pressed{
            border: 1px solid #2e6dcd; 
            background: #2e6dcd;
        }

        QPushbutton#pinfo_publish_btn:disabled{
            border: 1px solid #8cb8ea; 
            background: #98b9eb;
        }
        """
