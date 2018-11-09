from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (QScrollArea, QVBoxLayout, QFrame, QWidget,
                             QListWidget, QListWidgetItem, QLabel, QStackedLayout)
from cpchain.wallet.simpleqt.component import Component
from cpchain.wallet.simpleqt.decorator import component
from cpchain.wallet.pages import load_stylesheet, get_icon, app, HorizontalLine


class Banner(QFrame):

    def __init__(self, path, width, height, title, subtitle):
        self.width = width
        self.height = height
        self.path = path
        self.title = title
        self.subtitle = subtitle
        super().__init__()
        self.ui()
        self.style()

    # @component.method
    def brush(self):
        palette1 = QtGui.QPalette()
        palette1.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap(self.path)))
        self.setPalette(palette1)
        self.setAutoFillBackground(True)

    @component.ui
    def ui(self):
        if self.layout():
            QWidget().setLayout(self.layout())
        self.setMinimumWidth(self.width)
        self.setMaximumWidth(self.width)
        self.setMinimumHeight(self.height)
        self.setMaximumHeight(self.height)
        # self.brush()

        _main_layout = QStackedLayout()
        _main_layout.setContentsMargins(0, 0, 0, 0)
        _main_layout.setAlignment(Qt.AlignCenter)
        _main_layout.setStackingMode(QStackedLayout.StackAll)

        background = QLabel()
        pix = QtGui.QPixmap(self.path)
        pix = pix.scaled(self.width, self.height)
        background.setPixmap(pix)

        _main_layout.addWidget(background)

        mylayout = QVBoxLayout()
        title = QLabel(self.title)
        title.setObjectName('title')
        subtitle = QLabel(self.subtitle)
        subtitle.setObjectName('subtitle')
        subtitle.setMaximumWidth(self.width / 2)
        subtitle.setWordWrap(True)
        # 短横线
        line = HorizontalLine(color="white", wid=10)
        line.setMaximumWidth(58)
        line.setObjectName('line')
        mylayout.addWidget(title)
        mylayout.addWidget(subtitle)
        mylayout.addWidget(line)

        wid = QWidget()
        wid.setStyleSheet('background: transparent')
        wid.setLayout(mylayout)

        _main_layout.addWidget(wid)
        return _main_layout

    @component.style
    def style(self):
        return """
            QLabel {
                color:#ffffff;
                text-align:left;
                padding-left: 32px;
            }
            QLabel#title {
                padding-left: 28px;
                font-size: 32px;
            }
            QLabel#subtitle {
                font-size:20px;
            }
            QFrame#line {
                margin-left: 38px;
            }
        """
