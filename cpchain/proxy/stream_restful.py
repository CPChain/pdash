import json
import logging

from functools import wraps

from klein import Klein
from twisted.web.server import Site

from cpchain.utils import reactor

from cpchain import config
from cpchain.proxy.db import ProxyDB
from cpchain.kafka import KafkaProducer, KafkaConsumer

logger = logging.getLogger(__name__)

def json_response(func):
    """
    @json_response decorator adds response header for content type,
    and json-dumps response object.
    Example usage:
        @json_response
        def test(request):
            return { "key": "value" }
    """
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        res = func(self, request, *args, **kwargs)
        request.setHeader('Content-Type', 'application/json')
        return json.dumps(res)
    return wrapper

def catch_exceptions(func):
    """
    @catch_exceptions decorator handles generic exceptions in the request handler.
    All uncaught exceptions will be packaged into a nice JSON response, and returned
    to the caller with status code 500.
    """
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        try:
            res = func(self, request, *args, **kwargs)
        except Exception as e:
            logger.exception(e)
            request.setResponseCode(500)
            request.setHeader('Content-Type', 'application/json')
            return json.dumps({"error": str(e)})
        return res
    return wrapper

class RestfulServer:
    app = Klein()
    proxy_db = ProxyDB()

    @app.route('/<stream_id>')
    @catch_exceptions
    @json_response
    def stream_handle(self, request, stream_id):
        if not self.proxy_db.query_data_path(stream_id):
            return {'status': 'forbidden'}

        if request.method == b'GET':
            pass
        elif request.method == b'POST':
            data = request.content.read()

            brokers = config.proxy.kafka_brokers
            producer = KafkaProducer(brokers, stream_id)
            producer.produce(stream_id, data)
            producer.flush()

        return {'status': 'ok'}

    def run(self):
        port = config.proxy.server_stream_restful_port

        # here could not use app.run(), which calls reactor.run()
        # to start the event loop immediately.
        self.trans = reactor.listenTCP(port, Site(self.app.resource()))

    def stop(self):
        self.trans.stopListening()
