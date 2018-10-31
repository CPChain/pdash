import sys

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QMessageBox, QScrollArea,
                             QVBoxLayout, QWidget)

from .model import Model

sys.path.append('.')

class MsgSignals(QtCore.QObject):

    error = QtCore.pyqtSignal(str)

    info = QtCore.pyqtSignal(str)

    warning = QtCore.pyqtSignal(str)

class MessageBox:

    parent = None

    signals = MsgSignals()

    def __init__(self, parent=None):
        if parent:
            self.parent = parent
        self.signals.error.connect(self.error_)
        self.signals.info.connect(self.info_)
        self.signals.warning.connect(self.warning_)

    def error(self, content, title="Error"):
        self.signals.error.emit(content)

    def info(self, content, title="Info"):
        self.signals.info.emit(content)

    def warning(self, content, title="Warning"):
        self.signals.warning.emit(content)

    def error_(self, content):
        title = 'Error'
        QMessageBox.critical(self.parent, title, content)

    def info_(self, content):
        title = 'PDash'
        QMessageBox.information(self.parent, title, content)

    def warning_(self, content):
        title = "Warning"
        QMessageBox.warning(self.parent, title, content)


class Signals(QtCore.QObject):

    change = QtCore.pyqtSignal(object, name="modelChanged")

    click = QtCore.pyqtSignal(name="Click")

    disabled = QtCore.pyqtSignal(name='Diabled')

    refresh = QtCore.pyqtSignal(name='Refresh')

    loading = QtCore.pyqtSignal(name='loading')

    loading_over = QtCore.pyqtSignal(name='loading over')

    payed = QtCore.pyqtSignal(name="Payed")


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
