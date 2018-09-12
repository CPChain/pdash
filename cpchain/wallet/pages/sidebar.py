from PyQt5.QtWidgets import (QScrollArea, QVBoxLayout, QWidget, QFrame,
                             QListWidget, QListWidgetItem)

from cpchain.wallet.pages import load_stylesheet, get_icon


class SideBar(QScrollArea):
    def __init__(self, parent, main_wnd, menu):
        super().__init__(parent)
        self.parent = parent
        self.content_tabs = parent.content_tabs
        self.main_wnd = main_wnd
        self.menu = menu
        self.init_ui()

    def init_ui(self):

        self.setObjectName("sidebar")
        self.setMaximumWidth(201)

        self.frame = QFrame()
        self.setWidget(self.frame)
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(150)

        menuWidget = QListWidget()
        menuWidget.setMaximumHeight(100)
        link_map = dict()
        first = None
        for item in self.menu:
            menuWidget.addItem(QListWidgetItem(get_icon(item['icon']), item['name']))
            link_map[item['name']] = item['link']
            if not first:
                first = item['link']
        menuWidget.setContentsMargins(0, 0, 0, 0)
        menuWidget.setCurrentRow(0)

        def list_clicked(item):
            wid = self.content_tabs.findChild(QWidget, link_map[item.text()])
            self.content_tabs.setCurrentWidget(wid)
        menuWidget.itemPressed.connect(list_clicked)

        self.content_tabs.setCurrentWidget(self.content_tabs.findChild(QWidget, first))

        def set_layout():
            main_layout = QVBoxLayout(self.frame)
            main_layout.setContentsMargins(0, 0, 0, 0)

            main_layout.addSpacing(10)
            main_layout.addSpacing(3)
            main_layout.addWidget(menuWidget)
            main_layout.addSpacing(1)
            main_layout.addStretch(1)
            self.setLayout(main_layout)
        set_layout()
        load_stylesheet(self, "sidebar.qss")
