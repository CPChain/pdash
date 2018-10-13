from PyQt5 import QtCore
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
from cpchain.wallet.pages import main_wnd

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

class Table(TableWidget):

    change = QtCore.pyqtSignal(list, name="modelChanged")

    def __init__(self, parent, header=None, data=None, itemHandler=None, sort=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setFocusPolicy(Qt.NoFocus)

        # Set Header
        self.setHeader(header)
        # Set Data
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
                font-family: SFUIDisplay-Regular;
                font-size: 14px;
                padding-left: 12px;
                border: none;
                outline: none;
                outline-style: none;
                color: #1c1c1c;
                height: 31px;
            }

            QHeaderView::section{
                font-family: SFUIDisplay-Regular;
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
            item.setTextAlignment(Qt.AlignLeft)
            self.setHorizontalHeaderItem(i, item)
            self.setColumnWidth(i, header['width'][i])
            i += 1

    def setData(self, data, itemHandler):
        if not data:
            return
        data.setView(self)
        self.data = data.value
        row_number = len(data.value)
        self.setRowCount(row_number)
        for cur_row in range(row_number):
            items = itemHandler(self.data[cur_row])
            i = 0
            for item in items:
                if isinstance(item, str):
                    widget = QTableWidgetItem(item)
                    self.setItem(cur_row, i, widget)
                else:
                    self.setCellWidget(cur_row, i, item)
                i += 1
