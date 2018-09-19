from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel
from simpleqt.model import Model
from simpleqt.widgets import init

class Label(QLabel):

    change = QtCore.pyqtSignal(str, name="modelChanged")

    def __init__(self, *args, **kwargs):
        args, kwargs = init(self, *args, **kwargs)
        new_args = []
        for i in args:
            new_args.append(str(i))
        super().__init__(*new_args, **kwargs)
        self.change.connect(self.modelChange)

    def modelChange(self, value):
        self.setText(value)
