import time

from twisted.internet import threads
from twisted.internet.task import LoopingCall
from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory, connectWS

class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        self.running = True
        self.record_id = 0
        def produce_stream():
            record = 'record %d' % self.record_id
            self.record_id += 1
            print('sending record: {0}'.format(record))
            self.sendMessage(record.encode('utf8'))
        loop = LoopingCall(produce_stream)
        loop.start(2)

    def onMessage(self, payload, isBinary):

        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        self.running = False
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    if len(sys.argv) != 2:
        print("Need the WebSocket server address, i.e. ws://127.0.0.1:8002/80847d48-a43d-11e8-9cea-080027bea42a")
        sys.exit(1)

    factory = WebSocketClientFactory(sys.argv[1] + '?action=publish')
    factory.protocol = MyClientProtocol

    connectWS(factory)
    reactor.run()
