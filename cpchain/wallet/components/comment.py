from PyQt5.QtCore import (QObject, QPoint, Qt, QUrl, pyqtProperty, pyqtSignal, 
                          pyqtSlot)
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtWidgets import QVBoxLayout

from cpchain.wallet.pages import qml_path
from cpchain.wallet.simpleqt import Component


class Comment(Component):

    qml = qml_path('components/product/Comment.qml')

    def __init__(self, parent):
        self.obj = None
        super().__init__(parent)

    def ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        widget = QQuickWidget(self)
        widget.open()
        widget.setContentsMargins(0, 0, 0, 0)
        widget.rootContext().setContextProperty('self', self.obj)
        widget.setSource(QUrl(self.qml))
        layout.addWidget(widget)
        return layout
