
class Model:

    def __init__(self, value):
        self.value_ = value
        self.view = None

    @property
    def value(self):
        return self.value_

    @value.setter
    def value(self, val):
        self.value_ = val
        if self.view is not None:
            try:
                self.view.change.emit(val)
            except Exception as e:
                self.view.signals.change.emit(val)

    def plain_set(self, val):
        self.value_ = val

    def setView(self, view):
        self.view = view

class ListModel(Model):

    def __init__(self, value):
        super().__init__(value)
        self.index = 0 if value else -1

    def index_set(self, index):
        self.index = index

    @property
    def current(self):
        if self.index == -1:
            return None
        return self.value[self.index]
    
    def append(self, val):
        self.value_.append(val)
        if self.view:
            if self.view.change:
                self.view.change.emit(val)
