from PyQt5.QtCore import Qt, QObject, pyqtSlot, pyqtSignal, pyqtProperty
from cpchain.wallet.pages import abs_path, OrderStatus, app
from cpchain.wallet.simpleqt import Signals
import sys
sys.path.append('.')

class ImageObject(QObject):
    
    srcChanged = pyqtSignal()

    widthChanged = pyqtSignal()

    heightChanged = pyqtSignal()

    downloadingGifChanged = pyqtSignal()

    isDownloadingChanged = pyqtSignal()

    needMaskChanged = pyqtSignal()

    showTextChanged = pyqtSignal()
    
    def __init__(self, parent=None, src=None, width=None, height=None, market_hash=None, show_status=False):
        super().__init__(parent)
        self.src_ = src
        self.width_ = width
        self.height_ = height
        self.signals = Signals()
        self.status = None
        self.need_mask_ = True
        self.show_status = show_status
        status = app.get_status(market_hash, app.addr)
        if status is not None and self.show_status:
            self.status = app.get_status_enum(status)
        else:
            self.need_mask_ = False
        self.downloading_gif_ = abs_path('icons/downloading.gif')
        self.is_downloading_ = False
        self.show_text_ = ""
        self.init()

    def init(self):
        if not self.status:
            return
        if self.status == OrderStatus.created or self.status == OrderStatus.delivering:
            self.show_text_ = "To be delivered"
        elif self.status == OrderStatus.delivered:
            self.show_text_ = "To be received"
        elif self.status == OrderStatus.receiving or self.status == OrderStatus.received:
            self.is_downloading_ = True
        elif self.status == OrderStatus.confirmed:
            self.need_mask_ = False


    @pyqtProperty(str, notify=downloadingGifChanged)
    def downloading_gif(self):
        return self.downloading_gif_
    
    @pyqtProperty(bool, notify=isDownloadingChanged)
    def is_downloading(self):
        return self.is_downloading_
    
    @is_downloading.setter
    def is_downloading(self, value):
        if self.is_downloading_ == value:
            return
        self.is_downloading_ = value
        self.isDownloadingChanged.emit()
    
    @pyqtProperty(bool, notify=needMaskChanged)
    def need_mask(self):
        return self.need_mask_
    
    @need_mask.setter
    def need_mask(self, value):
        if self.need_mask_ == value:
            return
        self.need_mask_ = value
        self.needMaskChanged.emit()
    
    @pyqtProperty(str, notify=srcChanged)
    def src(self):
        return self.src_
    
    @src.setter
    def src(self, value):
        if self.src_ == value:
            return
        self.src_ = value
        self.srcChanged.emit()
    
    @pyqtProperty(str, notify=showTextChanged)
    def show_text(self):
        return self.show_text_
    
    @show_text.setter
    def show_text(self, value):
        if self.show_text_ == value:
            return
        self.show_text_ = value
        self.showTextChanged.emit()
    
    @pyqtProperty(str, notify=widthChanged)
    def width(self):
        return str(self.width_)
    
    @width.setter
    def width(self, value):
        value = str(value)
        if self.width_ == value:
            return
        self.width_ = value
        self.widthChanged.emit()
    
    @pyqtProperty(str, notify=heightChanged)
    def height(self):
        return str(self.height_)
    
    @height.setter
    def height(self, value):
        value = str(value)
        if self.height_ == value:
            return
        self.height_ = value
        self.heightChanged.emit()
    
    @pyqtSlot()
    def clickImage(self):
        self.signals.click.emit()

class ProductObject(QObject):
    
    def __init__(self, parent=None, width=None, height=None,
                 image=None, img_width=None, img_height=None):
        super().__init__(parent)
        self.image_ = ImageObject(parent, image, img_width, img_height)
    
    @pyqtProperty(QObject)
    def image(self):
        return self.image_
