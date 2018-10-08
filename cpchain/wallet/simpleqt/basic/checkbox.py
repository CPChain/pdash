from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt

from . import Builder, operate
from .. import Signals

class CheckBox(QCheckBox):
    
    signals = Signals()

    def __init__(self, model=None, *args, **kw):
        super().__init__(*args, **kw)
        self.model = model
        if model:
            model.setView(self)

        self.setStyleSheet(self.style())
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self.signals.change.connect(self.modelChange)
        self.toggled.connect(self.viewChange)

    class Builder(Builder):
        
        def __init__(self, widget=None):
            if not widget:
                widget = CheckBox
            self.widget = widget()
    
    def modelChange(self, value):
        self.setChecked(value)

    def viewChange(self):
        if self.model:
            self.model.plain_set(self.isChecked())

    def style(self):
        return """
            
        """
