import logging

from twisted.internet import threads
from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory, listenWS

from cpchain import config
from cpchain.proxy.db import ProxyDB
from cpchain.kafka import KafkaProducer, KafkaConsumer

logger = logging.getLogger(__name__)

class WSProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        logger.debug("Client connecting: %s" % request.peer)

        self.error_request = False

        try:
            self.stream_id = request.params['stream_id'][0]
            self.action = request.params['action'][0] # publish or subscribe
            if self.action not in ['publish', 'subscribe']:
                self.error_request = True

        except:
            self.error_request = True

        proxy_db = self.factory.proxy_db
        if not proxy_db.query_data_path(self.stream_id):
            self.error_request = True

        if self.error_request:
            raise Exception('wrong request params')

        else:
            brokers = config.proxy.kafka_brokers
            if self.action == 'publish':
                self.producer = KafkaProducer(brokers, str(request.peer))
            elif self.action == 'subscribe':
                self.consumer = KafkaConsumer(brokers, str(request.peer))

    def onOpen(self):
        logger.debug("WebSocket connection open.")

        def consume_stream():
            for record in self.consumer.consume([self.stream_id]):
                self.sendMessage(record)

        if self.action == 'subscribe':
            return threads.deferToThread(
                consume_stream
                )

    def onMessage(self, payload, isBinary):
        if self.action == 'publish':
            # just use stream id as topic
            self.producer.produce(self.stream_id, payload)

    def onClose(self, wasClean, code, reason):
        logger.debug("WebSocket connection closed: %s" % reason)
        if not self.error_request:
            if self.action == 'publish':
                self.producer.flush()
            elif self.action == 'subscribe':
                self.consumer.stop()


class WSServer:
    def __init__(self):

        port = config.proxy.server_stream_ws_port
        self.factory = WebSocketServerFactory(u"ws://0.0.0.0:%d" % port)
        self.factory.protocol = WSProtocol
        self.factory.proxy_db = ProxyDB()

        self.trans = None

    def run(self):
        self.trans = listenWS(self.factory)

    def stop(self):
        self.trans.stopListening()
