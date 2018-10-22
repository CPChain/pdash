from PyQt5.QtWidgets import QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from functools import wraps
from ..model import Model
from .. import Signals
import sys
sys.path.append('.')

class Binder:

    @staticmethod
    def click(obj, listener):
        setattr(obj, 'mousePressEvent', listener)

def operate(func):
    @wraps(func)
    def wrapper(*args, **kw):
        self = args[0]
        func(*args, **kw)
        return self
    return wrapper

class Line(QFrame):
    def __init__(self, parent=None, wid=2, color="#ccc"):
        super().__init__(parent)
        self.parent = parent
        self.wid = wid
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(self.wid)
        self.setStyleSheet("QFrame{{ border-top: {}px solid {};}}".format(wid, color))

class Builder:

    def __init__(self, widget=QLabel, *args, **kw):
        self.widget = widget("", *args, **kw)
        if widget == QLabel:
            self.widget.setTextInteractionFlags(Qt.TextSelectableByMouse)

    @operate
    def model(self, model):
        self.widget.model = model
        model.setView(self.widget)
        self.widget.setText(str(model.value))

    @operate
    def text(self, text):
        self.widget.setText(str(text))
    
    @operate
    def align(self, align):
        self.widget.setAlignment(align)

    @operate
    def wrap(self, wrap):
        self.widget.setWordWrap(wrap)

    @operate
    def width(self, width):
        self.widget.setMinimumWidth(width)

    @operate
    def height(self, height):
        self.widget.setMinimumHeight(height)

    @operate
    def name(self, name):
        self.widget.setObjectName(name)

    @operate
    def click(self, callback):
        if isinstance(self.widget, QLabel):
            Binder.click(self.widget, callback)
            self.widget.setCursor(QCursor(Qt.PointingHandCursor))
            return
        self.widget.clicked.connect(callback)

    @operate
    def pixmap(self, pixmap):
        self.widget.setPixmap(pixmap)

    def build(self):
        return self.widget

from .button import Button
from .input import Input
from .checkbox import CheckBox

def init(self, *args, **kwargs):
    new_args = []
    for i in args:
        if isinstance(i, Model):
            i.setView(self)
            new_args.append(i.value)
        else:
            new_args.append(i)
    return new_args, kwargs

class Label(QLabel):
    
    def __init__(self, *args, **kwargs):
        args, kwargs = init(self, *args, **kwargs)
        new_args = []
        for i in args:
            new_args.append(str(i))
        super().__init__(*new_args, **kwargs)
        self.signals = Signals()
        self.signals.change.connect(self.modelChange)

    def modelChange(self, value):
        self.setText(str(value))

__all__ = [Builder, Button, Input, CheckBox, Label]
