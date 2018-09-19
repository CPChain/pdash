
from PyQt5 import QtWidgets

class Page(QtWidgets.QScrollArea):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Execute Data
        self.data()
        # UI Compose
        self.ui()
        # Render
        self.style()
        # Init
        self.create()
