from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QLineEdit, QTextEdit, QCheckBox, QComboBox

from cpchain.wallet.simpleqt.model import Model

def init(self, *args, **kwargs):
    new_args = []
    for i in args:
        if isinstance(i, Model):
            i.setView(self)
            new_args.append(i.value)
        else:
            new_args.append(i)
    return new_args, kwargs

class Input(QLineEdit):

    change = QtCore.pyqtSignal(str, name="modelChanged")

    def __init__(self, *args, **kwargs):
        _args, _kwargs = init(self, *args, **kwargs)
        super().__init__(*_args, **_kwargs)
        self.change.connect(self.modelChange)
        self.editingFinished.connect(self.viewChange)
        for i in args:
            if isinstance(i, Model):
                self.model = i

    def modelChange(self, value):
        self.setText(value)

    def viewChange(self):
        self.model.plain_set(self.text())

class TextEdit(QTextEdit):

    change = QtCore.pyqtSignal(str, name="modelChanged")

    def __init__(self, *args, **kwargs):
        _args, _kwargs = init(self, *args, **kwargs)
        super().__init__(*_args, **_kwargs)
        self.change.connect(self.modelChange)
        self.textChanged.connect(self.viewChange)
        for i in args:
            if isinstance(i, Model):
                self.model = i

    def modelChange(self, value):
        self.setText(value)

    def viewChange(self):
        self.model.plain_set(self.toPlainText())


class CheckBox(QCheckBox):

    change = QtCore.pyqtSignal(str, name="modelChanged")

    def __init__(self, *args, **kwargs):
        new_args = []
        for i in args:
            if isinstance(i, Model):
                i.setView(self)
            else:
                new_args.append(i)
        super().__init__(*new_args, **kwargs)
        self.change.connect(self.modelChange)
        self.toggled.connect(self.viewChange)
        for i in args:
            if isinstance(i, Model):
                self.model = i

    def modelChange(self, value):
        self.setChecked(value)

    def viewChange(self):
        self.model.plain_set(self.isChecked())


class ComboBox(QComboBox):

    change = QtCore.pyqtSignal(list, name="modelChanged")

    def __init__(self, *args, **kwargs):
        new_args = []
        for i in args:
            if isinstance(i, Model):
                print(i)
                i.setView(self)
            else:
                new_args.append(i)
        super().__init__(*new_args, **kwargs)
        self.change.connect(self.modelChange)
        self.currentIndexChanged.connect(self.viewChange)
        for i in args:
            if isinstance(i, Model):
                self.model = i
        self.value = self.model.value[0] if self.model.value else None
        for val in self.model.value:
            self.addItem(val)

    def modelChange(self, value):
        for i in value:
            self.addItem(i)

    def viewChange(self, index):
        self.value = self.model.value[index]
        self.model.index_set(index)
