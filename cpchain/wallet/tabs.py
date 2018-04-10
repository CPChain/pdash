

from PyQt5.QtWidgets import (QScrollArea, QFormLayout, QVBoxLayout, QComboBox, QLineEdit, QLabel,
                             QTextEdit, QTableWidget, QPushButton, QTableWidgetItem, QAbstractItemView)

from PyQt5.QtCore import Qt, QPoint

from PyQt5.QtWidgets import QMenu, QAction, QHeaderView

from PyQt5.QtGui import QCursor

from cpchain.wallet.net import hoge


class TableWidget(QTableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)

    def set_right_menu(self, func):
        self.customContextMenuRequested[QPoint].connect(func)


from cpchain.wallet import net
class BrowseTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("browse_tab")
        self.init_ui()

    def init_ui(self):

        def create_item_table():
            self.item_table = item_table = TableWidget(self)
            item_table.setObjectName("item_table")


            # cf. https://stackoverflow.com/a/6840656/855160
            def right_menu():
                sel = item_table.selectionModel()
                if not sel.hasSelection():
                    return

                def buy_action():
                    hoge("hi")

                menu = QMenu(item_table)
                action = QAction("Buy", item_table, triggered=buy_action) 

                menu.addAction(action)
                menu.exec_(QCursor.pos())

            item_table.set_right_menu(right_menu)


            headers = ["Title", "Size", "Price"]
            item_table.setColumnCount(len(headers))
            item_table.setHorizontalHeaderLabels(headers)
            item_table.horizontalHeader().setStretchLastSection(True)
            # pending
            # https://stackoverflow.com/a/38129829/855160
            # header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

            item_table.setMinimumWidth(self.width())

            # item_table.setColumnWidth(0, self.width()/3*1.25)

            item_table.setAlternatingRowColors(True)

            # some tweaks
            item_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            item_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            # select only one row
            item_table.setSelectionMode(QAbstractItemView.SingleSelection)
            item_table.setShowGrid(False)

            # do not show row counts
            item_table.verticalHeader().setVisible(False)

        create_item_table()
        # oh. the heck.
        self.update_item_table()


        def set_layout():
            main_layout = QVBoxLayout(self)
            main_layout.addWidget(self.item_table)

        set_layout()


    def update_item_table(self):
        item_table = self.item_table
        item_table.insertRow(item_table.rowCount())
        item_table.setItem(0, 0, QTableWidgetItem("asdf"))
        item_table.setItem(0, 1, QTableWidgetItem("as"))
        item_table.setItem(0, 2, QTableWidgetItem("xx"))

            
class PublishTab(QScrollArea):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setObjectName("publish_tab")

        self.init_ui()

    def init_ui(self):

        def set_layout():
            main_layout = QFormLayout(self)
            self.data_item = QComboBox()
            self.data_title = QLineEdit()
            self.data_desc = QTextEdit()
            self.data_tags = QLineEdit()

            main_layout.addRow(QLabel("Data"), self.data_item)
            main_layout.addRow(QLabel("Title"), self.data_title)
            main_layout.addRow(QLabel("Description"), self.data_desc)
            main_layout.addRow(QLabel("Tag"), self.data_tags)


            publish_btn = QPushButton('Publish')
            publish_btn.clicked.connect(self.publish_data)

            main_layout.addWidget(publish_btn)

        set_layout()


    def publish_data(self):
        # mc = net.MarketClient()
        net.mc.publish_product('test', 'testdata', 13, 'temp', '2018-04-01 10:10:10', '2018-04-01 10:10:10', '123456')
        #print(type(self.data_title.text()))
