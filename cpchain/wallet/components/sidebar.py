from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (QScrollArea, QVBoxLayout, QWidget, QFrame,
                             QListWidget, QListWidgetItem)
from cpchain.wallet.simpleqt.component import Component
from cpchain.wallet.simpleqt.decorator import component
from cpchain.wallet.pages import load_stylesheet, get_icon, app


class SideBar(Component):
    def __init__(self, menu):
        self.menu = menu
        self.frame = None
        self.menuWidget = None
        super().__init__()

    @component.create
    def create(self):
        app.router.addListener(self.routerListener)

    # @component.method
    def routerListener(self, page):
        index = 0
        for item in self.menu:
            if item['link'] == page:
                self.menuWidget.setCurrentRow(index)
                break
            index += 1

    @component.ui
    def ui(self):
        self.setObjectName("sidebar")
        self.setMaximumWidth(201)

        menuWidget = QListWidget()
        menuWidget.setObjectName('menu')
        menuWidget.setFrameShape(QListWidget.NoFrame)
        menuWidget.setMinimumHeight(700)

        link_map = dict()
        for item in self.menu:
            menuWidget.addItem(QListWidgetItem(get_icon(item['icon']), item['name']))
            link_map[item['name']] = item['link']
        menuWidget.setCurrentRow(0)

        def list_clicked(item):
            app.router.redirectTo(link_map[item.text()])
        menuWidget.itemPressed.connect(list_clicked)
        menuWidget.setAttribute(Qt.WA_MacShowFocusRect, 0)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(menuWidget)
        main_layout.addStretch(1)
        self.menuWidget = menuWidget
        return main_layout

    @component.style
    def style(self):
        return """
        QVBoxLayout {
            background: red;
        }
        #sidebar {
            background: red;    
        }
        QFrame {
            background: #eee;
        }

        QListWidget#menu {
            font-family:SFUIDisplay-Regular;
            font-size:14px;
            color: #000000;
            border: none;
            outline: none;
            text-align: left;
        }

        QListWidget#menu::item  {
            padding: 8px 10px;
            color: #1c1c1c;
            border: 1px solid #eeeeee;
        }

        QListWidget#menu::item:selected  {
            background: #fafafa;
            border: 1px solid #fafafa;
        }
        """
