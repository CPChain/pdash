from PyQt5.QtWidgets import QLabel
from functools import wraps
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

class Builder:

    def __init__(self, widget=QLabel):
        self.widget = widget("")

    @operate
    def model(self, model):
        self.widget.model = model
        model.setView(self.widget)

    @operate
    def text(self, text):
        self.widget.setText(text)
    
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

__all__ = [Builder, Button, Input, CheckBox]
