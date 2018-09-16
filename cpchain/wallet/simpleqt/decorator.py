
from .model import Model
from functools import wraps

class page:
    
    @staticmethod
    def data(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            data = func(*args, **kwargs)
            for key in data:
                setattr(self, key, Model(data[key]))
        return wrapper
    
    @staticmethod
    def ui(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            layout = func(*args, **kwargs)
            self.setLayout(layout)
            return layout
        return wrapper
