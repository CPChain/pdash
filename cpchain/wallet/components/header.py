from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty

from cpchain.wallet.pages import qml_path, abs_path, app
from cpchain.wallet.simpleqt.component import Component
from cpchain.wallet.simpleqt.decorator import component

class HeaderObject(QObject):
    
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
    
    @pyqtProperty(str)
    def close_icon(self):
        return abs_path('icons/close.png')
    
    @pyqtProperty(str)
    def close_icon_hover(self):
        return abs_path('icons/closehover.png')
    
    @pyqtSlot()
    def close(self):
        app.main_wnd.close()

class Header(Component):
    
    qml = qml_path('components/Header.qml')

    def __init__(self, parent):
        self.obj = HeaderObject()
        super().__init__(parent)

    @component.create
    def create(self):
        pass

    @component.ui
    def ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        widget = QQuickWidget(self)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.rootContext().setContextProperty('self', self.obj)
        widget.setSource(QtCore.QUrl(self.qml))
        layout.addWidget(widget)
        return layout
