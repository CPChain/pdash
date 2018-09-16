from PyQt5 import QtCore
from simpleqt.model import Model

def init(self, *args, **kwargs):
    # 对 args 和 kwargs 进行处理，遇到 Model 时进行value替换
    new_args = []
    for i in args:
        if isinstance(i, Model):
            i.setView(self)
            new_args.append(i.value)
        else:
            new_args.append(i)
    return new_args, kwargs
