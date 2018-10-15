from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel
from simpleqt.model import Model
from simpleqt.widgets import init

from .. import Signals

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
        self.setText(value)
