
import logging
from queue import Queue
from twisted.internet.threads import deferToThread
from twisted.internet import reactor


logger = logging.getLogger(__name__)

class Event:
    pass

# Event Queue
event_queue = Queue()

# Handler
handler_map = dict()

def emit(event):
    event_queue.put(event)

def register(event, handler):
    handlers = handler_map.get(event, [])
    handlers.append(handler)
    handler_map[event] = handlers

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
