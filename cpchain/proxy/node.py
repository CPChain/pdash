import logging

import os

from twisted.internet import reactor, ssl
from twisted.web.server import Site
from twisted.internet.task import LoopingCall

from cpchain import config, root_dir
from cpchain.proxy.network import PeerProtocol
from cpchain.proxy.server import SSLServerFactory, FileServer

logger = logging.getLogger(__name__)

class Peer:
    def __init__(self, peer_port=None,
            ctrl_port=None, data_port=None):
        self.peer_port = peer_port or \
                config.proxy.server_peer_port
        self.ctrl_port = ctrl_port or \
                config.proxy.server_ctrl_port
        self.data_port = data_port or \
                config.proxy.server_data_port

        self.protocol = PeerProtocol(peer_info=self.ctrl_port)
        self.refresh_loop = LoopingCall(self.protocol.refresh_peers)

    def bootstrap(self, addr):
        if self.protocol.transport is None:
            return reactor.callLater(1, self.bootstrap)

        self.protocol.ping(addr)

    def run(self):

        self.refresh_loop.start(5)

        reactor.listenUDP(self.peer_port, self.protocol)

        self.start_ssl_server()

    def start_ssl_server(self):

        server_key = os.path.expanduser(
                        os.path.join(config.home,
                            config.proxy.server_key))
        server_crt = os.path.expanduser(
                        os.path.join(config.home,
                            config.proxy.server_crt))

        if not os.path.isfile(server_key):
            logger.info("SSL key/cert file not found, \
                    run local self-test by default")
            server_key = os.path.join(root_dir,
                    config.proxy.server_key)
            server_crt = os.path.join(root_dir,
                    config.proxy.server_crt)

        # ctrl channel
        factory = SSLServerFactory()
        reactor.listenSSL(self.ctrl_port, factory,
                ssl.DefaultOpenSSLContextFactory(
                server_key, server_crt))

        # data channel
        file_factory = Site(FileServer())
        reactor.listenSSL(self.data_port, file_factory,
                ssl.DefaultOpenSSLContextFactory(
                server_key, server_crt))


def find_peer(tracker):
    node = PeerProtocol()
    reactor.listenUDP(7890, node)

    def print_node(result):
        success, data = result
        if success:
            for peer in data:
                print(peer[0][0])
                print(peer[1])
        reactor.stop()

        node.transport.stopListening()

    node.select_peer(tracker).addCallback(print_node)


if __name__ == '__main__':
    import sys

    if sys.argv[1] == 'tracker':
        peer = Peer()
        peer.run()

    elif sys.argv[1] == 'peer':
        peer = Peer()
        peer.run()
        peer.bootstrap(('192.168.0.169', 5678))

    elif sys.argv[1] == 'client':
        tracker = ('192.168.0.169', 5678)
        find_peer(tracker)

    reactor.run()
