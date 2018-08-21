from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory, connectWS

class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    if len(sys.argv) != 2:
        print("Need the WebSocket server address, i.e. ws://127.0.0.1:8002?stream_id=80847d48-a43d-11e8-9cea-080027bea42a&action=subscribe")
        sys.exit(1)

    factory = WebSocketClientFactory(sys.argv[1])
    factory.protocol = MyClientProtocol

    connectWS(factory)
    reactor.run()
