#!/usr/bin/python3
import sys, os
import os.path as osp
import string


from PyQt5.QtWidgets import (QMainWindow, QApplication, QFrame, QDesktopWidget, QPushButton, QHBoxLayout,
                             QVBoxLayout, QGridLayout, QWidget, QScrollArea, QListWidget, QListWidgetItem, QTabWidget, QLabel,
                             QWidget, QLineEdit, QSpacerItem, QSizePolicy, QTableWidget, QFormLayout, QComboBox, QTextEdit,
                             QAbstractItemView, QTableWidgetItem, QMenu, QHeaderView, QAction, QFileDialog)
from PyQt5.QtCore import Qt, QSize, QPoint, pyqtSignal
from PyQt5.QtGui import QIcon, QCursor, QPixmap, QStandardItem, QFont

from cpchain import config, root_dir

# do it before any other twisted code.
def install_reactor():
    global app
    app = QApplication(sys.argv)
    import qt5reactor; qt5reactor.install()
install_reactor()

from twisted.internet import threads, defer
from twisted.internet.task import LoopingCall

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


# widgets

class TabContentArea(QFrame): pass

class PopularTab(TabContentArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("popular_tab")

        self.init_ui()

    def init_ui(self):

        def create_banner():
            self.banner_label = banner_label = QLabel(self)
            print("Getting banner images......")
            pixmap = QPixmap('cpc-logo-single.png')
            pixmap = pixmap.scaled(150, 100)
            banner_label.setPixmap(pixmap)
        create_banner()

        self.hot_label = QLabel("Hot")
        self.hot_label.setObjectName("hot_label")
        self.hot_label.setMaximumHeight(25)

        self.more_btn = more_btn = QPushButton("More", self)
        more_btn.setObjectName("more_btn")
        more_btn.setFixedSize(18, 18)

        def create_indus_trans():
            self.trans_label = trans_label = QLabel(self)
            print("Getting trans images......")
            pixmap = QPixmap('cpc-logo-single.png')
            pixmap = pixmap.scaled(75, 75)
            trans_label.setPixmap(pixmap)
        create_indus_trans()

        def create_indus_forest():
            self.forest_label = forest_label = QLabel(self)
            print("Getting trans images......")
            pixmap = QPixmap('cpc-logo-single.png')
            pixmap = pixmap.scaled(75, 75)
            forest_label.setPixmap(pixmap)
        create_indus_forest()

        def create_indus_medicine():
            self.medicine_label = medicine_label = QLabel(self)
            print("Getting trans images......")
            pixmap = QPixmap('cpc-logo-single.png')
            pixmap = pixmap.scaled(75, 75)
            medicine_label.setPixmap(pixmap)
        create_indus_medicine()

        self.recom_label = QLabel("Recommended")
        self.recom_label.setObjectName("recom_label")
        self.recom_label.setMaximumHeight(25)

        def set_layout():
            self.main_layout = QVBoxLayout(self)
            self.main_layout.addWidget(self.banner_label)
            self.main_layout.addSpacing(1)
            self.main_layout.addWidget(self.hot_label)

            self.hot_layout = QHBoxLayout(self)
            self.hot_layout.addSpacing(0)
            self.hot_layout.addWidget(self.hot_label)
            self.hot_layout.addSpacing(100)
            self.hot_layout.addWidget(more_btn)
            self.main_layout.addLayout(self.hot_layout)
            self.main_layout.addSpacing(1)

            self.hot_img_layout = QHBoxLayout(self)
            self.hot_img_layout.addSpacing(0)
            self.hot_img_layout.addWidget(self.trans_label)
            self.hot_img_layout.addSpacing(10)
            self.hot_img_layout.addWidget(self.forest_label)
            self.hot_img_layout.addSpacing(10)
            self.hot_img_layout.addWidget(self.medicine_label)
            self.main_layout.addLayout(self.hot_img_layout)
            self.main_layout.addSpacing(1)

            self.main_layout.addWidget(self.recom_label)

        set_layout()

        print("Loading stylesheet of cloud tab widget")


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

        def add_labels():
            self.trend_label = QLabel("Trending")
            self.trend_label.setObjectName("trend_label")
            self.trend_label.setMaximumHeight(25)

            self.mine_label = QLabel("Mine")
            self.mine_label.setObjectName("mine_label")
            self.trend_label.setMaximumHeight(25)

            self.treasure_label = QLabel("Treasure")
            self.treasure_label.setObjectName("treasure_label")
            self.treasure_label.setMaximumHeight(25)
        add_labels()

        def add_lists():
            self.trending_list = QListWidget()
            self.trending_list.addItem(QListWidgetItem(get_icon("pop.png"), "Popular"))
            self.trending_list.addItem(QListWidgetItem(get_icon("following.png"), "Following"))

            self.mine_list = QListWidget()
            self.mine_list.addItem(QListWidgetItem(get_icon("cloud.png"), "Cloud"))
            self.mine_list.addItem(QListWidgetItem(get_icon("store.png"), "Selling"))

            self.treasure_list = QListWidget()
            self.treasure_list.addItem(QListWidgetItem(get_icon("purchased.png"), "Purchased"))
            self.treasure_list.addItem(QListWidgetItem(get_icon("collection.png"), "Collection"))
            self.treasure_list.addItem(QListWidgetItem(get_icon("collection.png"), "Shopping Cart"))

            self.trending_list.setCurrentRow(0)
        add_lists()

        def bind_slots():
            def trending_list_clicked(item):
                item_to_tab_name = {
                    "Popular": "popular_tab",
                    "Following": "follow_tab",
                }
                wid = self.content_tabs.findChild(QWidget, item_to_tab_name[item.text()])
                self.content_tabs.setCurrentWidget(wid)
            self.trending_list.itemPressed.connect(trending_list_clicked)

            def mine_list_clicked(item):
                item_to_tab_name = {
                    "Cloud": "cloud_tab",
                    "Selling": "selling_tab",
                }
                wid = self.content_tabs.findChild(QWidget, item_to_tab_name[item.text()])
                self.content_tabs.setCurrentWidget(wid)
            self.mine_list.itemPressed.connect(mine_list_clicked)

            def treasure_list_clicked(item):
                item_to_tab_name = {
                    "Purchased": "purchase_tab",
                    "Collection": "collect_tab",
                    "Shopping Cart": "cart_tab",
                }
                wid = self.content_tabs.findChild(QWidget, item_to_tab_name[item.text()])
                self.content_tabs.setCurrentWidget(wid)
            self.treasure_list.itemPressed.connect(treasure_list_clicked)

        bind_slots()

        def set_layout():
            self.main_layout = main_layout = QVBoxLayout(self.frame)
            main_layout.addSpacing(0)
            main_layout.addWidget(self.trend_label)
            main_layout.addWidget(self.trending_list)
            main_layout.addWidget(self.mine_label)
            main_layout.addWidget(self.mine_list)
            main_layout.addWidget(self.treasure_label)
            main_layout.addWidget(self.treasure_list)
            main_layout.setContentsMargins(0, 10, 0, 0)
            self.setLayout(self.main_layout)
        set_layout()
        load_stylesheet(self, "sidebar.qss")
        print("Loading stylesheet of Sidebar")


class Header(QFrame):
    class SearchBar(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.init_ui()

        def init_ui(self):
            self.setObjectName("searchbar")
            self.setFixedSize(450, 25)
            self.setTextMargins(3, 0, 20, 0)

            self.search_btn = search_btn = QPushButton(self)
            search_btn.setObjectName("search_btn")
            search_btn.setFixedSize(18, 18)
            search_btn.setCursor(QCursor(Qt.PointingHandCursor))

            def bind_slots():
                print("Binding slots of clicked-search-btn......")
            bind_slots()

            def set_layout():
                main_layout = QHBoxLayout()
                main_layout.addStretch(1)
                main_layout.addWidget(search_btn)
                main_layout.setContentsMargins(0, 0, 0, 0)
                self.setLayout(main_layout)
            set_layout()


    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()


    def init_ui(self):
        def create_logos():
            self.logo_label = logo_label = QLabel(self)
            pixmap = QPixmap('cpc-logo-single.png')
            pixmap = pixmap.scaled(45, 45)
            logo_label.setPixmap(pixmap)
            self.word_label = QLabel(self)
            self.word_label.setText("<b>CPChain</b>")
            self.word_label.setFont(QFont("Roman times", 25, QFont.Bold));
            
            print("Pic label has not been set !")
        create_logos()

        def create_search_bar():
            self.search_bar = search_bar = Header.SearchBar(self)
            search_bar.setPlaceholderText("Search")
        create_search_bar()

        def create_btns():
            self.prev_btn = QPushButton("", self)
            self.prev_btn.setObjectName("prev_btn")

            self.nex_btn = QPushButton("", self)
            self.nex_btn.setObjectName("nex_btn")

            self.download_btn = QPushButton("", self)
            self.download_btn.setObjectName("download_btn")

            self.upload_btn = QPushButton("", self)
            self.upload_btn.setObjectName("upload_btn")

            self.message_btn = QPushButton("", self)
            self.message_btn.setObjectName("message_btn")

            self.profilepage_btn = QPushButton("", self)
            self.profilepage_btn.setObjectName("profilepage_btn")

            self.profile_btn = QPushButton("", self)
            self.profile_btn.setObjectName("profile_btn")

            def create_popmenu():
                self.profile_menu = profile_menu = QMenu('Profile', self)
                profile_view_act = QAction('Profile', self)
                pro_setting_act = QAction('Profile Settins', self)
                acc_setting_act = QAction('Account Settings', self)
                bill_man_act = QAction('Bill Management', self)
                help_act = QAction('Help', self)

                profile_menu.addAction(profile_view_act)
                profile_menu.addAction(pro_setting_act)
                profile_menu.addAction(acc_setting_act)
                profile_menu.addAction(bill_man_act)
                profile_menu.addAction(help_act)
            create_popmenu()
            self.profile_btn.setMenu(self.profile_menu)

        create_btns()


        def bind_slots():
            # TODO
            print("Binding slots of clicked-search-btn......")
            print("Binding slots of pre-btn......")
            print("Binding slots of nex-btn......")
        bind_slots()

        def set_layout():
            self.main_layout = main_layout = QHBoxLayout(self)
            #main_layout.setSpacing(0)
            main_layout.addWidget(self.logo_label)
            main_layout.addSpacing(5)
            main_layout.addWidget(self.word_label)
            main_layout.addSpacing(30)
            main_layout.addWidget(self.prev_btn)
            main_layout.addWidget(self.nex_btn)
            main_layout.addSpacing(2)
            main_layout.addWidget(self.search_bar)
            main_layout.addStretch(20)
            main_layout.addWidget(self.upload_btn)
            main_layout.addSpacing(10)
            main_layout.addWidget(self.message_btn)
            main_layout.addSpacing(10)
            main_layout.addWidget(self.download_btn)
            main_layout.addSpacing(10)
            main_layout.addWidget(self.profilepage_btn)
            main_layout.addSpacing(5)
            main_layout.addWidget(self.profile_btn)

            self.setLayout(self.main_layout)

        set_layout()

        # stylesheet
        #print("Setting header stylesheet......")
        load_stylesheet(self, "headertest.qss")

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
        # self.setWindowFlags(Qt.FramelessWindowHint)

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
            # Temporily modified for easy test by @hyiwr
            content_tabs.addTab(PopularTab(content_tabs), "")
            print("Adding tabs(cloud, browse, etc.) to content_tabs")
            print("Loading stylesheet to content_tabs")
        add_content_tabs()

        # add panes
        self.header = Header(self)
        self.sidebar = SideBar(self)


        # set layout
        def set_layout():
            self.main_layout = main_layout = QVBoxLayout()
            main_layout.addSpacing(0)
            main_layout.addWidget(self.header)

            self.content_layout = content_layout = QHBoxLayout()
            content_layout.addSpacing(0)
            content_layout.addWidget(self.sidebar)
            content_layout.addSpacing(0)
            content_layout.addWidget(self.content_tabs)

            self.main_layout.addLayout(self.content_layout)

            wid = QWidget(self)
            wid.setLayout(self.main_layout)
            self.setCentralWidget(wid)
        set_layout()
        load_stylesheet(self, "main_window.qss") 
        print("Seting stylesheet of MainWindow......")
          
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
        # Temporily modified for easy test by @hyiwr
        print("Initializing network......")
    initialize_net()
    
    def monitor_chain_event():
        # Temporily modified for easy test by @hyiwr
        print("Monitoring chain event......")
    monitor_chain_event()


def main():
    global main_wnd
    from twisted.internet import reactor
    main_wnd = MainWindow(reactor)
    _handle_keyboard_interrupt()

    initialize_system()
    
    sys.exit(reactor.run())


if __name__ == '__main__':
    main()
