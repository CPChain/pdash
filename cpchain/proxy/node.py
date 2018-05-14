import logging

import os

from twisted.internet import reactor, ssl
from twisted.web.server import Site
from twisted.internet.task import LoopingCall

from cpchain import config
from cpchain.proxy.network import PeerProtocol
from cpchain.proxy.server import SSLServerFactory, FileServer
from cpchain.utils import join_with_rc, join_with_root

logger = logging.getLogger(__name__)

class Peer:
    def __init__(self, peer_port=None,
                 ctrl_port=None, data_port=None):
        self.peer_port = (peer_port or
                          config.proxy.server_peer_port)
        self.ctrl_port = (ctrl_port or
                          config.proxy.server_ctrl_port)
        self.data_port = (data_port or
                          config.proxy.server_data_port)

        self.protocol = PeerProtocol(peer_info=self.ctrl_port)
        self.protocol.peer_stat = 0
        self.refresh_loop = LoopingCall(self.refresh)

        self.ctrl_factory = SSLServerFactory()

    def bootstrap(self, addr):
        if self.protocol.transport is None:
            return reactor.callLater(1, self.bootstrap)

        self.protocol.ping(addr)

    def refresh(self):
        self.protocol.refresh_peers()
        self.update_peer_stat()

    def update_peer_stat(self):
        if self.protocol.transport is None:
            return

        self.protocol.peer_stat = self.ctrl_factory.numConnections

    def run(self):

        self.refresh_loop.start(5)

        reactor.listenUDP(self.peer_port, self.protocol)

        self.start_ssl_server()

    def start_ssl_server(self):

        server_key = os.path.expanduser(
            join_with_rc(config.proxy.server_key))
        server_crt = os.path.expanduser(
            join_with_rc(config.proxy.server_crt))

        if not os.path.isfile(server_key):
            logger.info("SSL key/cert file not found, "
                        + "run local self-test by default")
            server_key = join_with_root(config.proxy.server_key)
            server_crt = join_with_root(config.proxy.server_crt)

        # ctrl channel
        reactor.listenSSL(self.ctrl_port, self.ctrl_factory,
                          ssl.DefaultOpenSSLContextFactory(
                              server_key, server_crt))

        # data channel
        file_factory = Site(FileServer())
        reactor.listenSSL(self.data_port, file_factory,
                          ssl.DefaultOpenSSLContextFactory(
                              server_key, server_crt))


def find_peer(boot_node, udp_port=7890):
    node = PeerProtocol()
    reactor.listenUDP(udp_port, node)

    def found_node(result):

        node.transport.stopListening()
        success, data = result
        if success:
            return tuple(data)

    d = node.select_peer(boot_node)
    d.addBoth(found_node)

    return d


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
        boot_node = ('192.168.0.169', 5678)
        def found_peer(peer):
            logger.info(peer)

        find_peer(boot_node).addCallback(found_peer)


    reactor.run()