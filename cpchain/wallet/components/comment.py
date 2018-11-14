from PyQt5.QtCore import (QObject, QPoint, Qt, QUrl, pyqtProperty, pyqtSignal,
                          pyqtSlot)
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtQuickWidgets import QQuickWidget

from cpchain.wallet.pages import qml_path, wallet, abs_path, Binder
from cpchain.wallet.simpleqt import Component, component
from cpchain.wallet.simpleqt.basic import Builder, Input, Text, Button

from .dialog import Dialog

class Star(QLabel):

    @staticmethod
    def load_star(path):
        pixmap = QPixmap(path)
        pixmap = pixmap.scaled(40, 40)
        return pixmap

    def __init__(self, star, listener):
        self.star = star
        self.listener = listener
        self.icon = Star.load_star(abs_path('icons/star_0@2x.png'))
        self.clicked_icon = Star.load_star(abs_path('icons/star_{}@2x.png'.format(star)))
        super().__init__()
        self.setPixmap(self.icon)
        self.is_clicked = False
        Binder.click(self, self.onClicked)
    
    def onClicked(self, _):
        if self.listener:
            self.listener(self.star)

    def onChangeStatus(self, now_star):
        if self.star <= now_star:
            self.is_clicked = True
        else:
            self.is_clicked = False
        icon = self.icon if not self.is_clicked else self.clicked_icon
        self.setPixmap(icon)


class Rate(Component):

    def __init__(self, *args, **kwargs):
        self.star = 0
        self.texts = ['Terrible', 'Cool', 'Average', 'Very good', 'Excellent']
        super().__init__(*args, **kwargs)
        self.setMinimumWidth(300)
    
    @component.data
    def data(self):
        return {
            "star_text": ""
        }

    def listener(self, star):
        self.star = star
        self.star_text.value = self.texts[self.star - 1]
        for widget in self.stars:
            widget.onChangeStatus(star)

    @component.ui
    def ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignLeft)
        layout.setSpacing(4)
        self.stars = [Star(i + 1, self.listener) for i in range(5)]
        for star in self.stars:
            layout.addWidget(star)
        text = Builder().model(self.star_text).style("color: #777; font-size: 14px").build()
        text.setMinimumHeight(40)
        layout.addSpacing(4)
        layout.addWidget(text)
        layout.addStretch(1)
        return layout
    

class CommentDialog(Dialog):

    def __init__(self, parent=None, oklistener=None):
        width = 474
        height = 394
        title = "Comfirmation"
        self.oklistener = oklistener
        self.data()
        super().__init__(wallet.main_wnd, title=title, width=width, height=height)

    @component.data
    def data(self):
        return {
            "password": "",
            "comment": ""
        }

    def gen_row(self, left_text, *widgets, **kw):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addSpacing(32)
        left_widget = Builder().text(left_text).name('left').style("font-size: 14px;").build()
        width = kw.get('left_width', 66)
        left_widget.setMinimumWidth(width)
        left_widget.setMaximumWidth(width)
        left_widget.setMinimumHeight(34)
        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.addWidget(left_widget)
        left.addStretch(1)
        row.addLayout(left)
        row.addSpacing(8)
        for widget in widgets:
            if isinstance(widget, QWidget):
                row.addWidget(widget)
                row.addSpacing(5)
        row.addStretch(1)
        return row

    def ui(self, widget):
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addSpacing(16)
        layout.addLayout(self.gen_row('Password:', Input.Builder(width=320, height=30)
                                                        .model(self.password)
                                                        .mode(Input.Password)
                                                        .placeholder("Please input password").build()))
        layout.addSpacing(40)
        layout.addLayout(self.gen_row('Rate:', Rate()))
        layout.addSpacing(16)
        layout.addLayout(self.gen_row('Comment:', Text.Builder(width=320, height=80)
                                                      .model(self.comment)
                                                      .placeholder("Your comment means a lot to all")
                                                      .build()))
        layout.addSpacing(40)

        bottom = QHBoxLayout()
        bottom.addStretch(1)
        bottom.setSpacing(20)
        btn_width = 80
        btn_height = 30
        bottom.addWidget(Button.Builder(width=btn_width, height=btn_height).click(self.cancel).text('Cancel').build())
        bottom.addWidget(Button.Builder(width=btn_width, height=btn_height).click(self.ok).style("primary").text('OK').build())
        bottom.addSpacing(32)

        layout.addLayout(bottom)
        layout.addSpacing(24)
        layout.addStretch(1)
        return layout

    def style(self):
        return super().style() + """
        """

    def cancel(self, _):
        self.close()

    def ok(self, _):
        self.close()
