#!/usr/bin/python3
import sys
import os.path as osp
import string
# from functools import partial

from PyQt5.QtWidgets import (QMainWindow, QApplication, QFrame, QDesktopWidget, QPushButton, QHBoxLayout,
                             QVBoxLayout, QGridLayout, QWidget, QScrollArea, QListWidget, QListWidgetItem, QTabWidget, QLabel,
                             QWidget, QLineEdit, QSpacerItem, QSizePolicy, QTableWidget, QFormLayout, QComboBox, QTextEdit,
                             QAbstractItemView, QTableWidgetItem, QMenu, QHeaderView, QAction)
from PyQt5.QtCore import Qt, QSize, QPoint 
from PyQt5.QtGui import QIcon, QCursor, QPixmap

# do it before any other twisted code.
def install_reactor():
    global app
    app = QApplication(sys.argv)
    import qt5reactor; qt5reactor.install()
install_reactor()

from cpchain import config, root_dir
from cpchain.utils import join_with_root
from cpchain.wallet.net import mc
from cpchain.wallet.net import foobar, login, hoge


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



class TableWidget(QTableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)

    def set_right_menu(self, func):
        self.customContextMenuRequested[QPoint].connect(func)


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
        mc.publish_product('test', 'testdata', 13, 'temp', '2018-04-01 10:10:10', '2018-04-01 10:10:10', '123456')
        #print(type(self.data_title.text()))

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

                def query():
                    # TOOD refactor this.
                    # switch to the browser pane
                    content_tabs = self.parent.parent.content_tabs
                    wid = content_tabs.findChild(QWidget, "browse_tab")
                    content_tabs.setCurrentWidget(wid)

                    # also update sidebar
                    sidebar = self.parent.parent.sidebar
                    item = sidebar.feature_list.findItems("Browse", Qt.MatchExactly)[0]
                    sidebar.feature_list.setCurrentItem(item)

                    return foobar(self.text())

                search_btn.clicked.connect(query)
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
            self.login_btn.clicked.connect(login)
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

            self.feature_list.setCurrentRow(0)
        add_lists()

        def bind_slots():
            def feature_list_clicked(item):
                item_to_tab_name = {
                    "Cloud Store": "cloud_tab",
                    "Publish Data": "publish_tab",
                    "Browse": "browse_tab",
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
            self.content_tabs = content_tabs = QTabWidget()
            content_tabs.tabBar().setObjectName("content_tabs")
            content_tabs.tabBar().hide()

            def create_file_tab():
                from cpchain.wallet.file_ui import FileTab
                t = FileTab(self)
                t.setObjectName("cloud_tab")
                return t

            content_tabs.addTab(create_file_tab(), "")
            content_tabs.addTab(PublishTab(self), "")
            content_tabs.addTab(BrowseTab(self), "")


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


        # stylesheets
        with open(join_with_root(config.wallet.qss.main_window)) as f:
            self.setStyleSheet(f.read())


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


def main():
    from twisted.internet import reactor
    main_wnd = MainWindow(reactor)
    _handle_keyboard_interrupt()
    sys.exit(reactor.run())


if __name__ == '__main__':
    main()
