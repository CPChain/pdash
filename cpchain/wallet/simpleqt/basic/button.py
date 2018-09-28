from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt

from . import Builder, operate

class Button(QPushButton):
    
    def __init__(self, text, width=228, height=38, *args, **kw):
        super().__init__(text, *args, **kw)
        self.width = width
        self.height = height
        self.setStyleSheet(self.blank_style())
    
    class Builder(Builder):
        
        def __init__(self):
            super().__init__(Button)
        
        @operate
        def style(self, _type):
            if _type == 'primary':
                self.widget.setStyleSheet(self.widget.primary_style())

    def primary_style(self):
        return self.blank_style() + """
            QPushButton {
                background: #167ce9;
                color: #fff;
            }
            QPushButton:hover, QPushButton:pressed {
                background: #187def;
                color: #fff
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

                font-family:SFUIDisplay-Medium;
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
    

