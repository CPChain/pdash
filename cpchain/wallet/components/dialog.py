from PyQt5.QtWidgets import QApplication, QScrollArea, QLabel, QVBoxLayout, QDialog, QWidget, QDesktopWidget
from PyQt5.QtCore import Qt, QEvent

class Dialog(QDialog):

    def __init__(self, parent, title="Title", width=500, height=180):
        self.parent = parent
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.center(width, height)
        self.setContentsMargins(0, 0, 0, 0)
        self.setAcceptDrops(True)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        # Title
        title = QLabel(title)
        title.setObjectName('title')
        layout.addWidget(title)
        widget = QWidget(self)
        self.main = self.ui(widget)
        widget.setObjectName('main')
        widget.setLayout(self.main)

        layout.addWidget(widget)
        self.setLayout(layout)
        self.setStyleSheet(self.style())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            QApplication.postEvent(self, QEvent(174))
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def center(self, width, height):
        geometry = self.parent.geometry()
        _w = geometry.width()
        _h = geometry.height()
        center_x = (_w - width) / 2
        center_y = (_h - height) / 2
        self.setGeometry(center_x, center_y, width, height)

    def ui(self, widget):
        main = QVBoxLayout(widget)
        main.addWidget(QLabel('Test'))
        return main

    def style(self):
        return """
            QDialog {
                background: #fafafa;
                border:1px solid #cccccc;
                border-radius:5px;
            }
            QLabel#title {
                background:#eeeeee;
                border:1px solid #cccccc;
                border-top-left-radius:5px;
                border-top-right-radius:5px;
                font-family:SFUIDisplay-Medium;
                font-size:16px;
                color:#333333;
                text-align:left;
                padding-top: 15px;
                padding-bottom:15px;
                padding-left: 15px;
            }
            QWidget#main Qlabel{
                font-family:SFUIDisplay-Regular;
                font-size:14px;
                color:#000000;
            }
        """
