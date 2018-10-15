from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt

from . import Builder, operate
from .. import Signals

class Input(QLineEdit):
    
    signals = Signals()

    def __init__(self, model=None, width=228, height=30, *args, **kw):
        if 'model' in kw:
            del kw['model']
        super().__init__(*args, **kw)
        self.model = model
        if model:
            model.setView(self)

        self.width = width
        self.height = height
        self.setStyleSheet(self.style())
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self.signals.change.connect(self.modelChange)
        self.textChanged.connect(self.viewChange)

    class Builder(Builder):
        
        def __init__(self, *args, **kw):
            super().__init__(Input, *args, **kw)
        
        @operate
        def placeholder(self, text):
            self.widget.setPlaceholderText(text)
        
        @operate
        def mode(self, mode):
            self.widget.setEchoMode(mode)
    
    def modelChange(self, value):
        self.setText(value)

    def viewChange(self):
        self.model.plain_set(self.text())

    def style(self):
        return """
            QLineEdit{{
                padding-left: 7px;
                padding-right: 7px;
                padding-top: 2px;
                padding-bottom: 1px;
                border:1px solid #ccc;
                border-radius: 5px;
                min-height: {height}px;
                max-height: {height}px;
                background: #ffffff;
                min-width: {width}px;
                max-width: {width}px;

                font-family:SFUIDisplay-Medium;
                font-size:14px;
                color:#9b9b9b;
            }}
        """.format(height=self.height, width=self.width)
