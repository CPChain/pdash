
import logging
from queue import Queue
from twisted.internet.threads import deferToThread
from twisted.internet import reactor
from functools import wraps


logger = logging.getLogger(__name__)

class Event:
    
    def __init__(self, data=None):
        self.data = data

# Event Queue
event_queue = Queue()

# Handler
handler_map = dict()

def emit(event, data=None):
    if event:
        event.data = data
    event_queue.put(event)

def _register(event, handler):
    handlers = handler_map.get(event, [])
    handlers.append(handler)
    handler_map[event] = handlers

def register(event, handler=None):
    if handler:
        return _register(event, handler)
    def func(handler):
        _register(event, handler)
        @wraps(handler)
        def wrapper(*args, **kw):
            return handler(*args, **kw)
        return wrapper
    return func

def run():
    while True:
        try:
            event = event_queue.get()
            handlers = handler_map.get(event, [])
            for handler in handlers:
                reactor.callWhenRunning(lambda: handler(event))
        except Exception as e:
            logger.error(e)

deferToThread(run)
