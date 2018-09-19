
from PyQt5 import QtWidgets

class Page(QtWidgets.QScrollArea):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 遍历所有经过装饰器装饰的函数
        # Execute Data
        self.data()
        # UI Compose
        self.ui()
        # Render
        self.style()
        # Init
        self.create()
