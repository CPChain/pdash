
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from . import Signals

class Page(QtWidgets.QScrollArea):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Execute Data
        self.data()
        # UI Compose
        ## if use qml
        self.ui()
        # Render
        self.style()
        # Init
        self.create()
        self.signals = Signals()
        self.signals.refresh.connect(self.ui)
    
    def data(self):
        pass
    
    def ui(self):
        pass
    
    def style(self):
        pass
    
    def create(self):
        pass

    def refresh(self):
        self.signals.refresh.emit()
        
