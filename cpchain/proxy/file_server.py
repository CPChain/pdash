import os
import logging

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
    server_root = join_with_rc(config.proxy.server_root)
    proxy_db = ProxyDB()

    def getChild(self, path, request):

        # don't expose the file list under root dir
        # for security consideration
        if path == b'':
            return ForbiddenResource()

        data_path = path.decode()
        file_path = os.path.join(self.server_root, data_path)
        return File(file_path)

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
