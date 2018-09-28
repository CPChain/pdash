from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore
import sys
sys.path.append('.')

class Signals(QtCore.QObject):

    change = QtCore.pyqtSignal(str, name="modelChanged")

def validate(self, validator, error, *args):
    if not validator(*args):
        QMessageBox.information(self, "Error", error)
        return False
    return True

from .model import Model

__all__ = [Model, Signals]
