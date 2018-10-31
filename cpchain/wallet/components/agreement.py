from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QFrame, QWidget, QCheckBox,
                             QListWidget, QListWidgetItem, QLabel)
from cpchain.wallet.simpleqt.component import Component
from cpchain.wallet.simpleqt.decorator import component
from cpchain.wallet.simpleqt.basic import CheckBox
from cpchain.wallet.simpleqt import Model
from cpchain.wallet.pages import load_stylesheet, get_icon, app, HorizontalLine


class Agreement(QWidget):

    def __init__(self, model, width, height):
        self.width = width
        self.height = height
        self.check = model or Model(False)
        super().__init__()
        self.ui()
        self.style()

    @property
    def checked(self):
        return self.check.value

    @component.ui
    def ui(self):
        self.setMinimumWidth(self.width)
        self.setMaximumWidth(self.width)
        self.setMinimumHeight(self.height)
        self.setMaximumHeight(self.height)
        aggHBox = QHBoxLayout()
        aggHBox.setContentsMargins(0, 0, 0, 0)
        aggHBox.setAlignment(Qt.AlignLeft)
        check = CheckBox(self.check)
        aggHBox.addWidget(check)
        aggHBox.addWidget(QLabel("I agree with"))
        agreement = QLabel("xxxxxx")
        agreement.setObjectName('agreement')
        aggHBox.addWidget(agreement)
        aggHBox.addStretch(1)
        return aggHBox


    @component.style
    def style(self):
        return """
            QLabel {
                font-size:12px;
                color:#101010;
                text-align:left;
            }
            #agreement {
                color: #3984f7;
            }
        """
