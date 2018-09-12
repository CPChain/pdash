import os
import logging
import cgi

from uuid import uuid1 as uuid

from twisted.web.resource import Resource, ForbiddenResource
from twisted.web.static import File
from twisted.web.server import Site
from twisted.internet import ssl

from cpchain import config
from cpchain.utils import join_with_rc
from cpchain.utils import reactor

from cpchain.proxy.ssl_cert import get_ssl_cert
from cpchain.proxy.db import ProxyDB

logger = logging.getLogger(__name__)

class FileServerResource(Resource):
    isLeaf = True
    server_root = join_with_rc(config.proxy.server_root)
    proxy_db = ProxyDB()

    def render_GET(self, request):
        path = request.path.decode().strip('/')

        # don't expose the file list under root dir
        # for security consideration
        if path == '':
            return ForbiddenResource().render(request)

        file_path = os.path.join(self.server_root, path)
        return File(file_path).render(request)

    def render_POST(self, request):
        headers = request.getAllHeaders()
        cgi_form = cgi.FieldStorage(
            fp=request.content,
            headers=headers,
            environ={
                'REQUEST_METHOD':'POST',
                'CONTENT_TYPE': headers[b'content-type'],
            }
        )
        # check <treq package>/multipart.py for request format details
        CRLF = "\r\n"
        file_content = cgi_form[' filename'].value.split(CRLF)[4:-2][0]

        server_root = join_with_rc(config.proxy.server_root)
        file_name = str(uuid())
        file_path = os.path.join(server_root, file_name)
        f = open(file_path, 'wb')
        f.write(file_content.encode('utf8'))
        f.close()

        return file_name.encode('utf8')

class FileServer:
    def __init__(self):
        self.trans = None
        self.port = config.proxy.server_file_port
        self.factory = Site(FileServerResource())

    def run(self):
        server_key, server_crt = get_ssl_cert()

        self.trans = reactor.listenSSL(
            self.port,
            self.factory,
            ssl.DefaultOpenSSLContextFactory(
                server_key,
                server_crt
                )
            )

    def stop(self):
        self.trans.stopListening()
