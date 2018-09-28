from PyQt5.QtWidgets import QMessageBox, QScrollArea, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
import sys
sys.path.append('.')

class Signals(QtCore.QObject):

    change = QtCore.pyqtSignal(str, name="modelChanged")

class Page(QScrollArea):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init()
        self.data()
        self.create()
        main = self.__ui()
        main.setContentsMargins(0, 0, 0, 0)
        self.layout = main
        self.hlayout = None
        self.layout.setAlignment(Qt.AlignCenter)
        self.ui(self.layout)
        main.addLayout(self.layout)
        self.setLayout(main)
        __style = self.__style()
        style = self.style()
        self.setStyleSheet(__style + style)
    
    def init(self):
        pass
    
    def data(self):
        pass
    
    def create(self):
        pass
    
    def __ui(self):
        return QVBoxLayout()
    
    def __style(self):
        return """
            QLabel {
                font-family:SFUIDisplay-Regular;
            }
        """
    
    def style(self):
        return ""
    
    def ui(self, layout):
        pass
    
    def add(self, elem, space=None):
        if isinstance(elem, QWidget):
            self.layout.addWidget(elem)
        else:
            self.layout.addLayout(elem)
        if space:
            self.spacing(space)
        self.hlayout = None
    
    def addH(self, elem, space=None):
        if not self.hlayout:
            self.hlayout = QHBoxLayout()
            self.hlayout.setAlignment(Qt.AlignLeft)
            self.layout.addLayout(self.hlayout)

        if isinstance(elem, QWidget):
            self.hlayout.addWidget(elem)
        else:
            self.hlayout.addLayout(elem)
        if space:
            self.hlayout.addSpacing(space)
    
    def spacing(self, space):
        self.layout.addSpacing(space)

def validate(self, validator, error, *args):
    if not validator(*args):
        QMessageBox.information(self, "Error", error)
        return False
    return True

from .model import Model

__all__ = [Model, Signals]
