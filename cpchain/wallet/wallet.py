#!/usr/bin/python3
import sys

from PyQt5.QtWidgets import (QMainWindow, QApplication, QFrame, QDesktopWidget, QPushButton, QHBoxLayout,
                             QVBoxLayout, QGridLayout, QWidget, QScrollArea, QListWidget, QListWidgetItem, QTabWidget, QLabel,
                             QWidget)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from cpchain import config
from cpchain.utils import join_with_root
from cpchain.wallet.tabs import PublishTab


class Header(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()


    def init_ui(self):

        def set_layout():
            self.main_layout = main_layout = QHBoxLayout(self)
            stub_label = QLabel("Stub")
            main_layout.addWidget(stub_label)
        set_layout()


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
        self.setMaximumWidth(200)

        self.frame = QFrame()
        self.setWidget(self.frame)
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(200)

        def add_btns():
            close_wnd_btn = QPushButton('✕', self)
            close_wnd_btn.setObjectName("close_wnd_btn")
            close_wnd_btn.setMaximumSize(18, 18)
            minimize_wnd_btn = QPushButton('_', self)
            minimize_wnd_btn.setObjectName("minimize_wnd_btn")
            minimize_wnd_btn.setMaximumSize(18, 18)
            maximize_wnd_btn = QPushButton('☐', self)
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
            btn_layout.setSpacing(5)
            btn_layout.addWidget(close_wnd_btn)
            btn_layout.addWidget(minimize_wnd_btn)
            btn_layout.addWidget(maximize_wnd_btn)
            btn_layout.addStretch(10)
            return btn_layout

        btn_layout = add_btns()


        def add_lists():
            self.feature_list = QListWidget()            
            self.feature_list.addItem("My Data")
            self.feature_list.addItem("Publish Data")
            self.feature_list.setCurrentRow(0)
        add_lists()


        def bind_slots():
            def feature_list_clicked(item):
                item_to_tab_name = {
                    "My Data": "data_tab",
                    "Publish Data": "publish_tab",
                }

                wid = self.content_tabs.findChild(QWidget, item_to_tab_name[item.text()])
                self.content_tabs.setCurrentWidget(wid)


            self.feature_list.itemPressed.connect(feature_list_clicked)

        bind_slots()


        def set_layout():
            self.main_layout = main_layout = QVBoxLayout(self.frame)
            main_layout.addLayout(btn_layout)
            main_layout.addWidget(self.feature_list)

            main_layout.setContentsMargins(0, 8, 0, 0)

            self.setLayout(self.main_layout)

        set_layout()


        with open(join_with_root(config.wallet.qss.sidebar)) as f:
            style = f.read()
            self.setStyleSheet(style)
            # self.frame.setStyleSheet(style)


class MainWindow(QMainWindow):
    def __init__(self, reactor):
        super().__init__()
        self.reactor = reactor
        self.init_ui()

        
    def init_ui(self):               
        # overall window settings
        self.setWindowTitle('CPChain Wallet')    
        self.setObjectName('MainWindow')
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

            def create_file_tab():
                from cpchain.wallet.file_ui import FileTab
                t = FileTab(self)
                t.setObjectName("data_tab")
                return t

            content_tabs.addTab(create_file_tab(), "")

            content_tabs.addTab(PublishTab(self), "")


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
            main_layout.setRowStretch(1, 7)

            
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
    app = QApplication(sys.argv)

    import qt5reactor
    qt5reactor.install()
    from twisted.internet import reactor

    main_wnd = MainWindow(reactor)

    _handle_keyboard_interrupt()
    sys.exit(reactor.run())


if __name__ == '__main__':
    main()
