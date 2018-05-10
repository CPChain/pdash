#!/usr/bin/python3
import sys, os
import os.path as osp
import string


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

#for temp test:
root_dir = "~/CPChain/cpchain/"
#

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
            pixmap = pixmap.scaled(32, 32)
            logo_label.setPixmap(pixmap)
            self.word_label = QLabel(self)
            self.word_label.setText("<b>CPChain</b>")
            print("Pic label has not been set !")
        create_logos()

        def create_search_bar():
            self.search_bar = search_bar = Header.SearchBar(self)
            search_bar.setPlaceholderText("Search")
        create_search_bar()

        def create_btns():
            self.prev_btn = QPushButton("<", self)
            self.prev_btn.setObjectName("prev_btn")

            self.nex_btn = QPushButton(">", self)
            self.nex_btn.setObjectName("nex_btn")

            self.download_btn = QPushButton("Download", self)
            self.download_btn.setObjectName("download_btn")

            self.upload_btn = QPushButton("Upload", self)
            self.upload_btn.setObjectName("upload_btn")

            self.message_btn = QPushButton("Message", self)
            self.message_btn.setObjectName("message_btn")

            self.profilepage_btn = QPushButton("Profile", self)
            self.profilepage_btn.setObjectName("profilepage_btn")

            self.profile_btn = QPushButton("▼", self)
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
            main_layout.setSpacing(0)
            main_layout.addWidget(self.logo_label)
            main_layout.addWidget(self.word_label)
            main_layout.addSpacing(60)
            main_layout.addWidget(self.prev_btn)
            main_layout.addWidget(self.nex_btn)
            main_layout.addSpacing(2)
            main_layout.addWidget(self.search_bar)
            main_layout.addStretch(20)
            main_layout.addWidget(self.download_btn)
            main_layout.addSpacing(1)
            main_layout.addWidget(self.upload_btn)
            main_layout.addSpacing(1)
            main_layout.addWidget(self.message_btn)
            main_layout.addSpacing(1)
            main_layout.addWidget(self.profilepage_btn)
            main_layout.addWidget(self.profile_btn)

            self.setLayout(self.main_layout)

        set_layout()

        # stylesheet
        print("Setting header stylesheet......")

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
            print("Adding tabs(cloud, browse, etc.) to content_tabs")
            print("Loading stylesheet to content_tabs")
        add_content_tabs()

        # add panes
        self.header = Header(self)

        # Temporily modified for easy test by @hyiwr
        print("Adding sidebar......")


        # set layout
        def set_layout():
            # cf. http://yu00.hatenablog.com/entry/2015/09/17/204338
            self.main_layout = main_layout = QGridLayout()
            main_layout.setSpacing(0)
            main_layout.setContentsMargins(0, 0, 0, 0)

            # Temporily modified for easy test by @hyiwr
            print("Adding widget sidebar......")
            main_layout.addWidget(self.header, 0, 1)
            # Temporily modified for easy test by @hyiwr
            print("Adding widget content_tabs......")

            main_layout.setRowStretch(0, 1)
            main_layout.setRowStretch(1, 9)

            wid = QWidget(self)
            wid.setLayout(self.main_layout)
            self.setCentralWidget(wid)
        set_layout()

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