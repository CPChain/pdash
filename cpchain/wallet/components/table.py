import importlib
import logging
import os
import os.path as osp
import string
from enum import Enum

from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor, QCursor, QFont, QFontDatabase
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QCheckBox, QDialog,
                             QFileDialog, QFrame, QGridLayout, QHBoxLayout,
                             QHeaderView, QLabel, QLineEdit, QListWidget,
                             QListWidgetItem, QMenu, QMessageBox, QPushButton,
                             QRadioButton, QScrollArea, QTableWidget,
                             QTableWidgetItem, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread

from cpchain import config, root_dir
from cpchain.crypto import ECCipher, Encoder, RSACipher
from cpchain.proxy.client import pick_proxy
from cpchain.utils import open_file, sizeof_fmt
from cpchain.wallet import fs
from cpchain.wallet.pages import (HorizontalLine, get_pixm, load_stylesheet,
                                  main_wnd, wallet)
from cpchain.wallet.simpleqt import Signals
from cpchain.wallet.simpleqt.model import Model

logger = logging.getLogger(__name__)

class ScrollStatus(Enum):
    TOP = 1
    BOTTOM = 2
    MIDDLE = 3

class TableWidget(QTableWidget):
    def __init__(self, parent=None):
        self.scroll_status = ScrollStatus.MIDDLE
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setHighlightSections(False)

        def scrolled(scrollbar, value):
            if value == scrollbar.maximum():
                self.scroll_status = ScrollStatus.BOTTOM
            elif value == scrollbar.minimum():
                self.scroll_status = ScrollStatus.TOP
            else:
                self.scroll_status = ScrollStatus.MIDDLE

        scrollBar = self.verticalScrollBar()
        scrollBar.valueChanged.connect(lambda value: scrolled(scrollBar, value))

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)


    def set_right_menu(self, func):
        self.customContextMenuRequested[QPoint].connect(func)

class Table(TableWidget):

    def __init__(self, parent, header=None, data=None, itemHandler=None, sort=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.row_number = 0
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setFocusPolicy(Qt.NoFocus)
        self.signals = Signals()
        self.signals.change.connect(self.change)

        # Set Header
        self.setHeader(header)
        # Set Data
        self.itemHandler = itemHandler
        self.setData(data, itemHandler)
        if header and data and sort:
            self.sortItems(sort)
        self.setStyleSheet("""
            QTableWidget {
                background: #ffffff;
                alternate-background-color: #f3f3f3;
                border: none;
                color: #676767;
            }

            QTableWidget::item.publish {
                color: blue;
            }

            QTableWidget::item {
                font-size: 14px;
                padding-left: 12px;
                border: none;
                outline: none;
                outline-style: none;
                color: #1c1c1c;
                height: 31px;
            }

            QHeaderView::section{
                font-size: 14px;
                padding-left: 15px;
                background: #f3f3f3;
                border: 0.5px solid #dcdcdc;
                height: 31px;
                font-weight: 300;
            }
        """)


    def setHeader(self, header):
        if not header:
            return
        self.header = header
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.NoSelection)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(30)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.setSortingEnabled(True)
        headers = header['headers']
        self.setColumnCount(len(headers))
        i = 0
        for label in headers:
            item = QTableWidgetItem(label)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.setHorizontalHeaderItem(i, item)
            self.setColumnWidth(i, header['width'][i])
            i += 1

    def change(self, value):
        logger.debug('Table Change')
        self.setData(value, self.itemHandler)
        logger.debug('Table Changed')

    def setData(self, data, itemHandler):
        logger.debug('Set Data')
        if not data:
            self.setMaximumHeight(40)
            return
        if not isinstance(data, list):
            data.setView(self)
            self.data = data.value
        else:
            self.data = data
        row_number = len(self.data)
        self.setRowCount(row_number)
        for cur_row in range(row_number):
            items = itemHandler(self.data[cur_row])
            i = 0
            for item in items:
                if isinstance(item, str):
                    widget = QTableWidgetItem(item)
                    self.setItem(cur_row, i, widget)
                else:
                    layout = QHBoxLayout()
                    layout.addWidget(item)
                    layout.setContentsMargins(0, 0, 0, 0)
                    widget = QWidget()
                    widget.setLayout(layout)
                    widget.setStyleSheet("background: {}".format("#f3f3f3" if cur_row % 2 else "#ffffff"))
                    self.setCellWidget(cur_row, i, widget)
                i += 1
        if row_number > 0:
            self.setMinimumHeight(180 if row_number > 5 else row_number * 30)
        else:
            self.setMaximumHeight(32)
        self.row_number = row_number

    def enterEvent(self, event):
        self.scroll_status = ScrollStatus.MIDDLE
        return super().enterEvent(event)

    def wheelEvent(self, event):
        if self.row_number <= 5:
            return self.parent.wheelEvent(event)
        else:
            return super().wheelEvent(event)
