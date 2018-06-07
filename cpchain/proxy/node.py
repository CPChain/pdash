import logging
import os
import asyncio

from twisted.internet import ssl, defer
from twisted.web.server import Site
from twisted.internet.task import LoopingCall

from kademlia.network import Server

from cpchain import config
from cpchain.utils import reactor
from cpchain.utils import join_with_rc, join_with_root
from cpchain.proxy.network import PeerProtocol
from cpchain.proxy.server import SSLServerFactory, FileServer
from cpchain.proxy.client import start_client
from cpchain.proxy.account import set_proxy_account, get_proxy_id, \
                                sign_proxy_data, derive_proxy_data

logger = logging.getLogger(__name__)


class KadServer(Server):
    def listen(self, port, interface='0.0.0.0'):
        """
        Start listening on the given port.

        Provide interface="::" to accept ipv6 address
        """
        loop = asyncio.get_event_loop()
        listen = loop.create_datagram_endpoint(self._create_protocol,
                                               local_addr=(interface, port))
        logger.info("Node %i listening on %s:%i",
                    self.node.long_id, interface, port)

        d = defer.Deferred()

        def create_endpoint_done(future):
            self.transport, self.protocol = future.result() # pylint: disable=attribute-defined-outside-init
            self.refresh_table()
            d.callback(True)

        future = asyncio.ensure_future(listen)
        future.add_done_callback(create_endpoint_done)

        return d

class Peer:
    def __init__(self):
        self.service_port = None
        self.peer_id = None
        self.ip = None

    def start_service(self, ip=None, ctrl_port=None, data_port=None, account_id=0):

        self.ip = ip
        set_proxy_account(account_id)
        self.peer_id = get_proxy_id()

        server_key = os.path.expanduser(
            join_with_rc(config.proxy.server_key))
        server_crt = os.path.expanduser(
            join_with_rc(config.proxy.server_crt))

        if not os.path.isfile(server_key):
            logger.info("SSL key/cert file not found, "
                        + "run local self-test by default")
            server_key_sample = 'cpchain/assets/proxy/key/server.key'
            server_crt_sample = 'cpchain/assets/proxy/key/server.crt'
            server_key = join_with_root(server_key_sample)
            server_crt = join_with_root(server_crt_sample)

        # data channel
        data_port = (data_port or config.proxy.server_data_port)
        file_factory = Site(FileServer())
        reactor.listenSSL(data_port, file_factory,
                          ssl.DefaultOpenSSLContextFactory(
                              server_key, server_crt))

        # ctrl channel
        ctrl_port = (ctrl_port or config.proxy.server_ctrl_port)
        ctrl_factory = SSLServerFactory(data_port=data_port)
        reactor.listenSSL(ctrl_port, ctrl_factory,
                          ssl.DefaultOpenSSLContextFactory(
                              server_key, server_crt))

        self.service_port = ctrl_port

        def set_proxy_ip():
            if self.ip is None:
                # waiting for node bootstrap finish
                return reactor.callLater(1, set_proxy_ip)

            ctrl_factory.set_external_ip(self.ip)

        set_proxy_ip()

    def join_centra_net(self, port=None, tracker=None):

        if tracker and not self.service_port:
            logger.error("proxy service not started")
            return

        port = port or config.proxy.server_peer_port
        protocol = PeerProtocol(
            peer_ip=self.ip,
            peer_id=self.peer_id,
            peer_info=self.service_port)
        reactor.listenUDP(port, protocol)

        def refresh():
            protocol.refresh_peers()

        if tracker:
            protocol.bootstrap(tracker)
        else:
            LoopingCall(refresh).start(5)

    def join_decentra_net(self, port=None, boot_nodes=None):

        if boot_nodes and not self.service_port:
            logger.error("proxy service not started")
            return

        port = (port or config.proxy.server_dht_port)

        peer = KadServer()

        if boot_nodes:

            d = defer.Deferred()

            def set_key_done(_):
                d.callback(True)

            def stun_done(future):
                addr = future.result()
                self.ip = addr[1][0]
                addr = '%s,%d' % (self.ip, self.service_port)

                asyncio.ensure_future(
                    peer.set(
                        self.peer_id,
                        sign_proxy_data(addr)
                        )
                    ).add_done_callback(set_key_done)

            def bootstrap_done(_):
                if self.ip:
                    addr = '%s,%d' % (self.ip, self.service_port)
                    asyncio.ensure_future(
                        peer.set(
                            self.peer_id,
                            sign_proxy_data(addr)
                            )
                        ).add_done_callback(set_key_done)
                else:
                    asyncio.ensure_future(
                        peer.protocol.stun(
                            boot_nodes[0]
                            )
                        ).add_done_callback(stun_done)

            def listen_done(_):
                asyncio.ensure_future(
                    peer.bootstrap(
                        boot_nodes
                        )
                    ).add_done_callback(bootstrap_done)

            peer.listen(port).addCallback(listen_done)

            return d

        return peer.listen(port)


    def pick_peer(self, tracker, port=None, sysconf=None):
        port = port or 8150
        protocol = PeerProtocol()
        reactor.listenUDP(port, protocol)

        d = defer.Deferred()

        def stop_listening_done(_, result):
            success, data = result
            if success and data:
                d.callback(data)
            else:
                d.callback(None)

        def pick_peer_done(result):
            protocol.transport.stopListening().addCallback(
                stop_listening_done, result)

        protocol.pick_peer(tracker, sysconf).addCallback(pick_peer_done)
        return d

    def get_peer(self, peer_id, tracker=None, boot_nodes=None, port=None):

        if isinstance(tracker, tuple):
            port = port or 8150
            protocol = PeerProtocol()
            reactor.listenUDP(port, protocol)

            d = defer.Deferred()

            def stop_listening_done(_, result):
                success, data = result
                if success and data:
                    d.callback(data)
                else:
                    d.callback(None)

            def get_peer_done(result):
                protocol.transport.stopListening().addCallback(
                    stop_listening_done, result)

            protocol.get_peer(peer_id, tracker).addCallback(get_peer_done)
            return d

        elif isinstance(boot_nodes, list):
            port = port or 8250

            peer = KadServer()

            d = defer.Deferred()

            def get_key_done(future):
                value = future.result()
                peer.stop()
                if value:
                    addr = derive_proxy_data(value)
                    d.callback(tuple(addr.split(',')))
                else:
                    d.callback(None)

            def bootstrap_done(_):
                asyncio.ensure_future(
                    peer.get(peer_id)
                    ).add_done_callback(get_key_done)

            def listen_done(_):
                asyncio.ensure_future(
                    peer.bootstrap(
                        boot_nodes
                        )
                    ).add_done_callback(bootstrap_done)

            peer.listen(port).addCallback(listen_done)

            return d

        else:
            logger.error("wrong tracker/boot nodes")

def pick_proxy(tracker=None, sysconf=None):
    if tracker is None:
        addr, port = config.proxy.tracker.split(':')
        tracker = (str(addr), int(port))

    # pick a proxy from tracker
    return Peer().pick_peer(
        tracker=tracker,
        sysconf=sysconf
        )

def start_proxy_request(sign_message, proxy_id, tracker=None, boot_nodes=None):

    if tracker is None and boot_nodes is None:
        addr, port = config.proxy.tracker.split(':')
        tracker = (str(addr), int(port))

        boot_nodes = []
        nodes = (config.proxy.boot_nodes.split())
        for node in nodes:
            addr, port = node.split(':')
            boot_nodes.append((str(addr), int(port)))

    d = defer.Deferred()

    def start_client_done(proxy_reply):
        d.callback(proxy_reply)

    def get_proxy_done(addr):
        if addr:
            start_client(sign_message, addr).addCallback(start_client_done)
        else:
            d.errback('failed to get proxy')

    def get_proxy(tracker, boot_nodes, proxy_id):
        # find the (ip, port) for given proxy
        return Peer().get_peer(
            peer_id=proxy_id,
            tracker=tracker,
            boot_nodes=boot_nodes
        )

    get_proxy(tracker, boot_nodes, proxy_id).addCallback(get_proxy_done)

    return d
