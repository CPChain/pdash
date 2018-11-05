from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QDialog, QWidget, QHBoxLayout, QFrame, QGraphicsDropShadowEffect, QStackedLayout
from PyQt5.QtCore import Qt, QEvent

from cpchain.wallet.pages import app
from cpchain.wallet.simpleqt.basic import Builder

class Dialog(QDialog):

    NO_SHADOW = False

    def __init__(self, parent, title="Title", width=500, height=180):
        self.parent = parent
        self.dragPosition = None
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.center(width + 10, height + 10)
        self.setAcceptDrops(True)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        # Title
        title = QLabel(title)
        title.setObjectName('title')
        def trigger_close(_):
            self.close()
        close_btn = Builder().text('x').name('close_btn').click(trigger_close).build()
        header = QHBoxLayout()
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(close_btn)
        self.close_btn = close_btn

        dlgHeader = QFrame()
        dlgHeader.setObjectName('header')
        dlgHeader.setMaximumWidth(width)
        dlgHeader.setLayout(header)
        layout.addWidget(dlgHeader)
        widget = QWidget(self)
        self.main = self.ui(widget)
        widget.setObjectName('main')
        widget.setLayout(self.main)
        widget.setMaximumWidth(width)
        layout.addWidget(widget)

        _main = QWidget()
        _main.setContentsMargins(0, 0, 0, 10)
        _main.setLayout(layout)
        _main.setStyleSheet(self.style())
        _main.setWindowOpacity(0.5)

        _main_layout = QStackedLayout()
        _main_layout.setContentsMargins(20, 20, 20, 20)
        _main_layout.setAlignment(Qt.AlignCenter)
        _main_layout.setStackingMode(QStackedLayout.StackAll)

        _backgound = QFrame()
        _backgound.setMinimumWidth(width)
        _backgound.setMinimumHeight(height)
        _backgound.setMaximumWidth(width)
        _backgound.setMaximumHeight(height)
        _backgound.setStyleSheet("background: #fafafa; border-radius:5px;")

        if not app.is_windows():
            _main_layout.addWidget(_backgound)
        _main_layout.addWidget(_main)

        self.setLayout(_main_layout)

        self.effect = QGraphicsDropShadowEffect(_backgound)
        self.effect.setOffset(0, 0)
        self.effect.setBlurRadius(30)
        # self.effect.setEnabled(False)
        _backgound.setGraphicsEffect(self.effect)

    def gen_row(self, left_text, *widgets, **kw):
        row = QHBoxLayout()

        left_widget = Builder().text(left_text).name('left').build()
        width = kw.get('left_width', 140)
        left_widget.setMinimumWidth(width)
        left_widget.setMaximumWidth(width)
        row.addWidget(left_widget)
        for widget in widgets:
            if isinstance(widget, QWidget):
                row.addWidget(widget)
        row.addStretch(1)
        return row

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            QApplication.postEvent(self, QEvent(174))
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if hasattr(self, 'dragPosition'):
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
                /*background: #fafafa;*/
                background: blue;
                border:1px solid #cccccc;
                border-radius:5px;
            }
            QWidget#main {
                background:#fafafa;
                border:1px solid #cccccc;
                border-bottom-left-radius:5px;
                border-bottom-right-radius:5px;

            }
            QFrame#header {
                background:#eeeeee;
                border:1px solid #cccccc;
                border-top-left-radius:5px;
                border-top-right-radius:5px;
                text-align:left;
                padding-top: 5px;
                padding-bottom:5px;
                padding-left: 15px;
                padding-right: 15px;
            }
            QLabel#title {
                font-size:16px;
                color:#333333;
                font-weight: 500;
            }
            QLabel#close_btn {
                font-size: 16px;
                color: #ee4040;
            }
            QWidget#main Qlabel{
                font-size:14px;
                color:#000000;
            }
        """
