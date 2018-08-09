import json
import logging

from functools import wraps

from klein import Klein

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
    def wrapper(request, *args, **kwargs):
        res = func(request, *args, **kwargs)
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
    def wrapper(request, *args, **kwargs):
        try:
            res = func(request, *args, **kwargs)
        except Exception as e:
            logger.exception(e)
            request.setResponseCode(500)
            request.setHeader('Content-Type', 'application/json')
            return json.dumps({"error": str(e)})
        return res
    return wrapper


app = Klein()

@app.route('/stream_order', methods=['POST'])
@catch_exceptions
@json_response
def order_post(request):
    data = json.loads(request.content.read())
    return {'status': 'success', 'stream_id': 'stream_id'}

@app.route('/stream/<stream_id>', methods=['POST'])
@catch_exceptions
@json_response
def stream_post(request, stream_id):
    data = json.loads(request.content.read())

    return {
        "status": 'success'
    }

@app.route('/stream/<stream_id>', methods=['GET'])
@catch_exceptions
@json_response
def echo_post(request, stream_id):
    data = json.loads(request.content.read())

    return {
        "status": 'success'
    }

app.run("localhost", 8300)
