from PyQt5.QtWidgets import QMessageBox, QScrollArea, QVBoxLayout, QWidget, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
import sys
sys.path.append('.')

class Signals(QtCore.QObject):

    change = QtCore.pyqtSignal(object, name="modelChanged")

    click = QtCore.pyqtSignal(name="Click")

    disabled = QtCore.pyqtSignal(name='Diabled')

    refresh = QtCore.pyqtSignal(name='Refresh')

    loading = QtCore.pyqtSignal(name='loading')

    loading_over = QtCore.pyqtSignal(name='loading over')

class Page(QScrollArea):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.parent = parent
        self.init()
        self.data()
        self.create()
        
        main = self.__ui()
        main.setContentsMargins(0, 0, 0, 0)

        self._layout = main
        self.hlayout = None
        self._layout.setAlignment(Qt.AlignCenter)
        self.ui(self._layout)


        __style = self.__style()
        style = self.style()
        self.setStyleSheet(__style + style)
        
        wid = QWidget()
        wid.setStyleSheet("background: #fafafa;")
        wid.setLayout(main)
        wid.setContentsMargins(0, 0, 0, 0)
        self.setWidget(wid)
    
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
            QScrollArea {
                background: #fafafa;
            }
            QLabel {
                font-family:SFUIDisplay-Regular;
            }
        """
    
    def style(self):
        return ""
    
    def ui(self, layout):
        pass
    
    def add(self, elem=None, space=None):
        if elem:
            if isinstance(elem, QWidget):
                self._layout.addWidget(elem)
            else:
                self._layout.addLayout(elem)
        if space:
            self.spacing(space)
        self.hlayout = None
    
    def addH(self, elem, space=None, align=None):
        if not self.hlayout:
            self.hlayout = QHBoxLayout()
            self.hlayout.setSpacing(0)
            self.hlayout.setAlignment(Qt.AlignLeft)
            self._layout.addLayout(self.hlayout)
        if align:
            self.hlayout.setAlignment(align)
        if isinstance(elem, QWidget):
            self.hlayout.addWidget(elem)
        else:
            self.hlayout.addLayout(elem)
        if space:
            self.hlayout.addSpacing(space)
    
    def spacing(self, space):
        self._layout.addSpacing(space)

def validate(self, validator, error, *args):
    if not validator(*args):
        QMessageBox.information(self, "Error", error)
        return False
    return True


from .model import Model

__all__ = [Model, Signals]
