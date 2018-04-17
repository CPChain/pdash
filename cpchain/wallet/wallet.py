#!/usr/bin/python3
import sys, os
import os.path as osp
import string
# from functools import partial

from PyQt5.QtWidgets import (QMainWindow, QApplication, QFrame, QDesktopWidget, QPushButton, QHBoxLayout,
                             QVBoxLayout, QGridLayout, QWidget, QScrollArea, QListWidget, QListWidgetItem, QTabWidget, QLabel,
                             QWidget, QLineEdit, QSpacerItem, QSizePolicy, QTableWidget, QFormLayout, QComboBox, QTextEdit,
                             QAbstractItemView, QTableWidgetItem, QMenu, QHeaderView, QAction, QFileDialog)
from PyQt5.QtCore import Qt, QSize, QPoint, pyqtSignal
from PyQt5.QtGui import QIcon, QCursor, QPixmap, QStandardItem

# do it before any other twisted code.
def install_reactor():
    global app
    app = QApplication(sys.argv)
    import qt5reactor; qt5reactor.install()
install_reactor()

from twisted.internet import threads, defer
from twisted.internet.task import LoopingCall

from cpchain import config, root_dir
# from cpchain.wallet.net import market_client, buyer_chain_client, seller_chain_client, test_chain_event
from cpchain.wallet.net import MarketClient, BuyerChainClient, SellerChainClient
from cpchain.wallet.fs import get_file_list, upload_file_ipfs, get_buyer_file_list
from cpchain.wallet.proxy_request import send_request_to_proxy
from cpchain.utils import join_with_root, sizeof_fmt, open_file


# utils
def get_icon(name):
    path = osp.join(root_dir, "cpchain/assets/wallet/icons", name)
    return QIcon(path)



def load_stylesheet(wid, name):
    path = osp.join(root_dir, "cpchain/assets/wallet/qss", name)

    subs = dict(asset_dir=osp.join(root_dir, "cpchain/assets/wallet"))

    with open(path) as f:
        s = string.Template(f.read())
        wid.setStyleSheet(s.substitute(subs))



class ComboBox(QComboBox):
    pop_up = pyqtSignal()

    def showPopup(self):
        self.pop_up.emit()
        super().showPopup()



class TableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        # size
        self.setMinimumWidth(self.parent.width())
        # context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        # do not highlight (bold-ize) the header
        self.horizontalHeader().setHighlightSections(False)


    def set_right_menu(self, func):
        self.customContextMenuRequested[QPoint].connect(func)



class TabContentArea(QFrame): pass


class CloudTab(TabContentArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("cloud_tab")

        self.hashcode = 'DEADBEEF'
        self.local_file = 'local'
        self.init_ui()

    def update_table(self):
        file_list = get_file_list()
        print(file_list.__len__())
        for cur_row in range(self.row_number):
            if cur_row == file_list.__len__():
                break
            self.file_table.setItem(cur_row, 0, QTableWidgetItem(file_list[cur_row].name))
            self.file_table.setItem(cur_row, 1, QTableWidgetItem(sizeof_fmt(file_list[cur_row].size)))
            self.file_table.setItem(cur_row, 2, QTableWidgetItem(file_list[cur_row].remote_type))
            self.file_table.setItem(cur_row, 3, QTableWidgetItem(str(file_list[cur_row].is_published)))
            self.file_table.setItem(cur_row, 4, QTableWidgetItem(file_list[cur_row].hashcode))

    def init_ui(self):
        self.row_number = 20

        def create_file_table():
            self.file_table = file_table = TableWidget(self)

            file_table.setColumnCount(5)
            file_table.setRowCount(self.row_number)
            file_table.setHorizontalHeaderLabels(['File Name', 'File Size', 'Remote Type', 'Published', 'Hash Code'])

            file_list = get_file_list()
            for cur_row in range(self.row_number):
                if cur_row == len(file_list):
                    break
                file_table.setItem(cur_row, 0, QTableWidgetItem(file_list[cur_row].name))
                self.file_table.setItem(cur_row, 1, QTableWidgetItem(sizeof_fmt(file_list[cur_row].size)))
                self.file_table.setItem(cur_row, 2, QTableWidgetItem(file_list[cur_row].remote_type))
                self.file_table.setItem(cur_row, 3, QTableWidgetItem(str(file_list[cur_row].is_published)))
                self.file_table.setItem(cur_row, 4, QTableWidgetItem(file_list[cur_row].hashcode))
        create_file_table()


        def handle_upload():
            # Maybe useful for buyer.
            # row_selected = self.file_table.selectionModel().selectedRows()[0].row()
            # selected_fpath = self.file_table.item(row_selected, 2).text()
            self.local_file = QFileDialog.getOpenFileName()[0]
            defered = threads.deferToThread(upload_file_ipfs, self.local_file)
            defered.addCallback(handle_callback_upload)

        def handle_callback_upload(x):
            print("in handle_callback_upload" + x)
            self.update_table()

        def create_btns():
            self.upload_btn = upload_btn = QPushButton('Encrypt and Upload')
            upload_btn.setObjectName("upload_btn")
            upload_btn.clicked.connect(handle_upload)
        create_btns()

        def set_layout():
            self.main_layout = QVBoxLayout(self)
            self.main_layout.addWidget(self.file_table)

            layout = QHBoxLayout()
            layout.addStretch(1)
            layout.addWidget(self.upload_btn)
            self.main_layout.addLayout(layout)

        set_layout()

        load_stylesheet(self, "cloud_tab.qss")



class TreasureTab(TabContentArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("treasure_tab")

        self.hashcode = 'DEADBEEF'
        self.local_file = 'local'
        self.init_ui()


    def update_table(self):
        file_list = get_buyer_file_list()
        print(file_list.__len__())
        for cur_row in range(self.row_number):
            if cur_row == file_list.__len__():
                break
            self.file_table.setItem(cur_row, 0, QTableWidgetItem(file_list[cur_row].name))
            self.file_table.setItem(cur_row, 1, QTableWidgetItem(sizeof_fmt(file_list[cur_row].size)))
            self.file_table.setItem(cur_row, 2, QTableWidgetItem(str(file_list[cur_row].is_downloaded)))
            self.file_table.setItem(cur_row, 3, QTableWidgetItem(file_list[cur_row].hashcode))


    def init_ui(self):
        self.row_number = 20

        def create_file_table():
            self.file_table = file_table = TableWidget(self)

            def right_menu():
                sel = file_table.selectionModel()
                if not sel.hasSelection():
                    return

                def open_file_action():
                    open_file('/home/introom/downloads/xx.txt')

                    row = file_table.currentRow()
                    # TODO note it's 2 because of the skew of INDEX.
                    col = file_table.columnCount()-2
                    cur_item = file_table.item(row, col)
                    # buyer_chain_client.buy_product(cur_item.text())

                menu = QMenu(file_table)
                action = QAction("Open File", file_table, triggered=open_file_action)

                menu.addAction(action)
                menu.exec_(QCursor.pos())
            file_table.set_right_menu(right_menu)



            file_table.setColumnCount(4)
            file_table.setRowCount(self.row_number)
            file_table.setHorizontalHeaderLabels(['File Name', 'File Size', 'Downloaded', 'Hash Code'])

            file_list = get_buyer_file_list()
            for cur_row in range(self.row_number):
                if cur_row == len(file_list):
                    break
                file_table.setItem(cur_row, 0, QTableWidgetItem(file_list[cur_row].name))
                self.file_table.setItem(cur_row, 1, QTableWidgetItem(sizeof_fmt(file_list[cur_row].size)))
                self.file_table.setItem(cur_row, 2, QTableWidgetItem(str(file_list[cur_row].is_downloaded)))
                self.file_table.setItem(cur_row, 3, QTableWidgetItem(file_list[cur_row].hashcode))

        create_file_table()


        def set_layout():
            self.main_layout = QVBoxLayout(self)
            self.main_layout.addWidget(self.file_table)
            layout = QHBoxLayout()
            layout.addStretch(1)
            self.main_layout.addLayout(layout)
        set_layout()



class BrowseTab(TabContentArea):
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
                    item_table = self.item_table
                    row = item_table.currentRow()
                    # TODO note it's 2 because of the skew of INDEX.
                    col = item_table.columnCount()-2
                    cur_item = item_table.item(row, col)
                    buyer_chain_client.buy_product(cur_item.text())

                menu = QMenu(item_table)
                action = QAction("Buy", item_table, triggered=buy_action)

                menu.addAction(action)
                menu.exec_(QCursor.pos())

            item_table.set_right_menu(right_menu)

            headers = ["Title", "Price", "Hash", "INDEX"]
            item_table.setColumnCount(len(headers))
            item_table.setHorizontalHeaderLabels(headers)
            item_table.horizontalHeader().setStretchLastSection(True)
            # use it as the reference.
            item_table.setColumnHidden(item_table.columnCount()-1, True)

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

        def set_layout():
            main_layout = QVBoxLayout(self)
            main_layout.addWidget(self.item_table)

        set_layout()


    def update_item_table(self, items):
        item_table = self.item_table

        def add_to_table(item):
            title = item['title']
            description = item['description']
            tags = item['tags']
            price = item['price']
            item_hash = item['msg_hash']
            id = item['id']
            seller_address = item['owner_address']

            row_cnt = item_table.rowCount()
            item_table.insertRow(row_cnt)

            j = 0
            def append_col(value):
                nonlocal j
                item_table.setItem(row_cnt, j, QTableWidgetItem(str(value)))
                j += 1

            append_col(title)
            append_col(price)
            # append_col(tags)
            append_col(item_hash)

        # clear content first.
        item_table.setRowCount(0)
        for item in items:
            add_to_table(item)



class PublishTab(TabContentArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("publish_tab")
        self.init_ui()

    def init_ui(self):

        def populate_data_item():
            # clear
            self.data_item.clear()

            model = self.data_item.model()
            uploaded_file_list = get_file_list()
            for cur_row in range(10):
                if cur_row == len(uploaded_file_list):
                    break
                item = QStandardItem(str(cur_row))
                item2 = QStandardItem(uploaded_file_list[cur_row].name)
                model.appendRow([item, item2])
                

        def create_data_item():
            # data item column
            self.data_item = ComboBox()
            model = self.data_item.model()
            model.setColumnCount(2)
            self.data_item.setModelColumn(1)
            # populuate initial data
            populate_data_item()
        create_data_item()


        def bind_slots():
            self.data_item.pop_up.connect(populate_data_item)
        bind_slots()


        def set_layout():
            main_layout = QFormLayout(self)

            self.data_title = QLineEdit()
            self.data_desc = QTextEdit()

            self.data_price = QLineEdit()
            self.data_price.setObjectName("data_price")
            self.data_price.setFixedWidth(100)

            self.data_tags = QLineEdit()
            self.data_tags.setFixedWidth(100)

            main_layout.addRow(QLabel("Data"), self.data_item)
            main_layout.addRow(QLabel("Title"), self.data_title)
            main_layout.addRow(QLabel("Description"), self.data_desc)
            main_layout.addRow(QLabel("Price"), self.data_price)
            main_layout.addRow(QLabel("Tag"), self.data_tags)

            publish_btn = QPushButton('Publish')
            publish_btn.setObjectName("publish_btn")
            publish_btn.clicked.connect(self.publish_data)
            layout = QHBoxLayout()
            layout.addStretch(1)
            layout.addWidget(publish_btn)
            main_layout.addRow(layout)

        set_layout()

        load_stylesheet(self, "publish_tab.qss")

    def publish_data(self):
        # def publish_product(self, title, description, price, tags, start_date, end_date, file_md5):
        title = self.data_title.text()
        description = self.data_desc.toPlainText()
        price = int(self.data_price.text())
        tags = self.data_tags.text()
        seller_file_id = self.data_item.currentIndex()
        print(seller_file_id)

        d = market_client.publish_product(seller_file_id, title, description, price, tags, '2018-04-01 10:10:10', '2018-04-01 10:10:10', '123456')

        def update_cloud_table(*args):
            wid = self.parent.findChild(QWidget, "cloud_tab")
            wid.update_table()
        d.addCallback(update_cloud_table)



class Header(QFrame):
    class SearchBar(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.init_ui()

        def init_ui(self):
            self.setObjectName("searchbar")
            self.setFixedSize(150, 25)
            self.setTextMargins(3, 0, 20, 0)

            self.search_btn = search_btn = QPushButton(self)
            search_btn.setObjectName("search_btn")
            search_btn.setFixedSize(18, 18)
            search_btn.setCursor(QCursor(Qt.PointingHandCursor))

            def bind_slots():

                def switch_to_browser_pane():
                    # TOOD refactor this.
                    # switch to the browser pane
                    content_tabs = self.parent.parent.content_tabs
                    wid = content_tabs.findChild(QWidget, "browse_tab")
                    content_tabs.setCurrentWidget(wid)
                    # also update sidebar
                    sidebar = self.parent.parent.sidebar
                    item = sidebar.feature_list.findItems("Browse", Qt.MatchExactly)[0]
                    sidebar.feature_list.setCurrentItem(item)

                @defer.inlineCallbacks
                def query():
                    switch_to_browser_pane()
                    items = yield market_client.query_product(self.text())

                    content_tabs = self.parent.parent.content_tabs
                    browse_tab = content_tabs.findChild(QWidget, "browse_tab")
                    browse_tab.update_item_table(items)

                # TODO i don't understand why this doesn't work.
                # search_btn.clicked.connect(query)
                search_btn.clicked.connect(lambda : query())
                self.returnPressed.connect(query)

            bind_slots()

            def set_layout():
                main_layout = QHBoxLayout()
                main_layout.addStretch(1)
                main_layout.addWidget(search_btn)
                # main_layout.addStretch(10)
                main_layout.setContentsMargins(0, 0, 0, 0)
                self.setLayout(main_layout)
            set_layout()


    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()


    def init_ui(self):
        def create_search_bar():
            self.search_bar = search_bar = Header.SearchBar(self)
            search_bar.setPlaceholderText("Search")
        create_search_bar()

        def create_btns():
            self.login_btn = QPushButton("▼ Login", self)
            self.login_btn.setObjectName("login_btn")
        create_btns()

        def bind_slots():
            # TODO
            self.login_btn.clicked.connect(lambda: market_client.login())

        bind_slots()

        def set_layout():
            self.main_layout = main_layout = QHBoxLayout(self)
            main_layout.setSpacing(0)
            main_layout.addWidget(self.search_bar)
            main_layout.addStretch(20)
            main_layout.addWidget(self.login_btn)

        set_layout()

        # stylesheet
        load_stylesheet(self, "header.qss")


    # drag support
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.m_DragPosition = event.globalPos() - self.parent.pos()
            self.parent.m_drag = True
            event.accept()


    def mouseMoveEvent(self, event):
        try:
            if Qt.LeftButton and event.buttons():
                self.parent.move(event.globalPos()-self.parent.m_DragPosition)
                event.accept()

        except AttributeError:
            pass


    def mouseReleaseEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.m_drag = False



class SideBar(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        # needed
        self.parent = parent
        self.content_tabs = parent.content_tabs

        self.init_ui()


    def init_ui(self):
        self.setObjectName("sidebar")
        self.setMaximumWidth(180)

        self.frame = QFrame()
        self.setWidget(self.frame)
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(150)

        def add_wnd_btns():
            close_wnd_btn = QPushButton('', self)
            close_wnd_btn.setObjectName("close_wnd_btn")
            close_wnd_btn.setMaximumSize(18, 18)

            minimize_wnd_btn = QPushButton('', self)
            minimize_wnd_btn.setObjectName("minimize_wnd_btn")
            minimize_wnd_btn.setMaximumSize(18, 18)

            maximize_wnd_btn = QPushButton('', self)
            maximize_wnd_btn.setObjectName("maximize_wnd_btn")
            maximize_wnd_btn.setMaximumSize(18, 18)

            # actions
            close_wnd_btn.clicked.connect(self.parent.close)
            minimize_wnd_btn.clicked.connect(self.parent.showMinimized)

            def toggle_maximization():
                state = Qt.WindowFullScreen | Qt.WindowMaximized
                if state & self.parent.windowState():
                    self.parent.showNormal()
                else:
                    self.parent.showMaximized()
            maximize_wnd_btn.clicked.connect(toggle_maximization)

            # layout
            btn_layout = QHBoxLayout()
            btn_layout.addSpacing(5)
            btn_layout.setSpacing(0)
            btn_layout.addWidget(close_wnd_btn)
            btn_layout.addWidget(minimize_wnd_btn)
            btn_layout.addWidget(maximize_wnd_btn)
            btn_layout.addStretch(10)
            return btn_layout

        btn_layout = add_wnd_btns()


        def add_lists():
            self.feature_list = QListWidget()
            # TODO adjust icon and text spacing.
            self.feature_list.addItem(QListWidgetItem(get_icon("cloud_store.png"), "Cloud Store"))
            self.feature_list.addItem(QListWidgetItem(get_icon("publish_data.png"), "Publish Data"))
            self.feature_list.addItem(QListWidgetItem(get_icon("browse_market.png"), "Browse"))
            self.feature_list.addItem(QListWidgetItem(get_icon("treasure.png"), "Treasure"))

            self.feature_list.setCurrentRow(0)
        add_lists()

        def bind_slots():
            def feature_list_clicked(item):
                item_to_tab_name = {
                    "Cloud Store": "cloud_tab",
                    "Publish Data": "publish_tab",
                    "Browse": "browse_tab",
                    "Treasure": "treasure_tab",
                }
                wid = self.content_tabs.findChild(QWidget, item_to_tab_name[item.text()])
                self.content_tabs.setCurrentWidget(wid)
            self.feature_list.itemPressed.connect(feature_list_clicked)
        bind_slots()

        def set_layout():
            self.main_layout = main_layout = QVBoxLayout(self.frame)
            main_layout.addLayout(btn_layout)
            main_layout.addSpacing(10)
            main_layout.addWidget(self.feature_list)
            main_layout.setContentsMargins(0, 10, 0, 0)
            self.setLayout(self.main_layout)
        set_layout()

        load_stylesheet(self, "sidebar.qss")



class MainWindow(QMainWindow):
    def __init__(self, reactor):
        super().__init__()
        self.reactor = reactor
        self.init_ui()


    def init_ui(self):
        # overall window settings
        self.setWindowTitle('CPChain Wallet')
        self.setObjectName("main_window")
        # no borders.  we make our own header panel.
        self.setWindowFlags(Qt.FramelessWindowHint)

        def set_geometry():
            self.resize(1000, 600)  # resize before centering.
            center_pt = QDesktopWidget().availableGeometry().center()
            qrect = self.frameGeometry()
            qrect.moveCenter(center_pt)
            self.move(qrect.topLeft())
        set_geometry()

        def add_content_tabs():
            self.content_tabs = content_tabs = QTabWidget(self)
            content_tabs.setObjectName("content_tabs")
            content_tabs.tabBar().hide()

            content_tabs.addTab(CloudTab(content_tabs), "")
            content_tabs.addTab(PublishTab(content_tabs), "")
            content_tabs.addTab(BrowseTab(content_tabs), "")
            content_tabs.addTab(TreasureTab(content_tabs), "")
            load_stylesheet(content_tabs, "content_tabs.qss")

        add_content_tabs()


        # def add_component(name, cls, *args):
        #     setattr(self, name, cls(self, *args))
        # add_component('header', Header)

        # add panes
        self.header = Header(self)
        self.sidebar = SideBar(self)


        # set layout
        def set_layout():
            # cf. http://yu00.hatenablog.com/entry/2015/09/17/204338
            self.main_layout = main_layout = QGridLayout()
            main_layout.setSpacing(0)
            main_layout.setContentsMargins(0, 0, 0, 0)

            main_layout.addWidget(self.sidebar, 0, 0, 2, 1)
            main_layout.addWidget(self.header, 0, 1)

            main_layout.addWidget(self.content_tabs, 1, 1)

            main_layout.setRowStretch(0, 1)
            main_layout.setRowStretch(1, 9)

            wid = QWidget(self)
            wid.setLayout(self.main_layout)
            self.setCentralWidget(wid)
        set_layout()

        load_stylesheet(self, "main_window.qss")

        self.show()


    def closeEvent(self, event):
        self.reactor.stop()



def _handle_keyboard_interrupt():
    def sigint_handler(*args):
        QApplication.quit()

    import signal
    signal.signal(signal.SIGINT, sigint_handler)

    # cf. https://stackoverflow.com/a/4939113/855160
    from PyQt5.QtCore import QTimer

    # make it global, o.w. the timer will soon vanish.
    _handle_keyboard_interrupt.timer = QTimer()
    timer = _handle_keyboard_interrupt.timer
    timer.start(300) # run each 300ms
    timer.timeout.connect(lambda: None)


    
def initialize_system():
    def initialize_net():
        global market_client, buyer_chain_client, seller_chain_client
        market_client = MarketClient(main_wnd)
        buyer_chain_client = BuyerChainClient(main_wnd, market_client)
        seller_chain_client = SellerChainClient(main_wnd, market_client)
    initialize_net()
    
    def monitor_chain_event():
        seller_poll_chain = LoopingCall(seller_chain_client.send_request)
        seller_poll_chain.start(10)
        buyer_check_confirm = LoopingCall(buyer_chain_client.check_confirm)
        buyer_check_confirm.start(15)
    monitor_chain_event()


def main():
    global main_wnd
    from twisted.internet import reactor
    main_wnd = MainWindow(reactor)
    _handle_keyboard_interrupt()

    initialize_system()

    # import logging
    # a = logging.Logger.manager.loggerDict.keys()
    # print(a)
    # logger = logging.getLogger("web3.providers.rpc")  # adjust logger name
    # # noisyLogger.getEffectiveLevel()  # indicates the current effective level
    # logger.setLevel(logging.INFO)
    import logging
    logging.disable(2222222222222222)

    
    sys.exit(reactor.run())



if __name__ == '__main__':
    main()
