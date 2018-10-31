from PyQt5.QtWidgets import QPushButton, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from . import Builder, operate

class Button(QPushButton):
    
    NO_TRANSPARENT = 0.9999

    def __init__(self, text, width=228, height=38, *args, **kw):
        super().__init__(text, *args, **kw)
        self.width = width
        self.height = height
        self.op = QGraphicsOpacityEffect(self)
        self.op.setOpacity(self.NO_TRANSPARENT)
        self.setGraphicsEffect(self.op)
        self.setAutoFillBackground(True)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(self.blank_style())
    
    class Builder(Builder):
        
        def __init__(self, *args, **kw):
            super().__init__(Button, *args, **kw)
        
        @operate
        def style(self, _type):
            if _type == 'primary':
                self.widget.setStyleSheet(self.widget.primary_style())
        
        @operate
        def width(self, width):
            self.widget.setMinimumWidth(width)
            self.widget.setMaximumWidth(width)

        @operate
        def height(self, height):
            self.widget.setMinimumHeight(height)
    
    def setEnabled(self, status):
        super().setEnabled(status)
        self.op.setOpacity(0.5 if not status else self.NO_TRANSPARENT)

    def primary_style(self):
        # background:rgb(22,124,233)
        return self.blank_style() + """
            QPushButton {
                background: #167ce9;
                color: #fff;
            }
            QPushButton:hover, QPushButton:pressed {
                background: #187def;
                color: #fff;
            }
        """

    def blank_style(self):
        return """
            QPushButton{{
                padding-left: 10px;
                padding-right: 10px;
                padding-top: 1px;
                padding-bottom: 1px;
                border:1px solid #0073df;
                border-radius:5px;
                min-height: {height}px;
                max-height: {height}px;
                background: #ffffff;
                min-width: {width}px;
                max-width: {width}px;
                font-size:15px;
                color:#0073df;
                text-align:center;
            }}

            QPushButton:hover{{
                border: 1px solid #3984f7; 
                color: #3984f6;
            }}

            QPushButton:pressed{{
                border: 1px solid #2e6dcd; 
                color: #2e6dcd;
                background: #e5ecf4;
            }}

            QPushbutton:disabled{{
                border: 1px solid #8cb8ea; 
                color: #8cb8ea;
            }}
        """.format(height=self.height, width=self.width)
    

