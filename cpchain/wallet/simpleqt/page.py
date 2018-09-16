
from PyQt5 import QtWidgets

class Page(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        # 遍历所有经过装饰器装饰的函数
        self.data()
        self.ui()