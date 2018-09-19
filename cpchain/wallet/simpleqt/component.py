
from PyQt5 import QtWidgets

class Component(QtWidgets.QWidget):

    def has(self, name):
        return hasattr(self, name)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Execute Data
        if self.has('data'):
            self.data()
        # UI Compose
        if self.has('ui'):
            self.ui()
        # Render
        if self.has('style'):
            self.style()
        # Init
        if self.has('create'):
            self.create()
