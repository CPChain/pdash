import logging
import asyncio

from twisted.internet import defer

from kademlia.network import Server

from cpchain import config

from cpchain.proxy.account import get_proxy_id, sign_proxy_data, derive_proxy_data

logger = logging.getLogger(__name__)

class KadNode(Server):
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

    def first_node(self):
        port = config.proxy.server_kad_port + 1
        return self.listen(port)

    def run(self):
        boot_nodes = []
        nodes = (config.proxy.boot_nodes.split())
        for node in nodes:
            addr, port = node.split(':')
            port = int(port)
            boot_nodes.append((str(addr), int(port)))

        proxy_id = get_proxy_id()

        d = defer.Deferred()

        def set_key_done(_):
            d.callback(True)

        def stun_done(future):
            addr = future.result()
            ip = addr[1][0]
            addr = '%s,%d' % (ip, config.proxy.server_port)

            asyncio.ensure_future(
                self.set(
                    proxy_id,
                    sign_proxy_data(addr)
                    )
                ).add_done_callback(set_key_done)

        def bootstrap_done(_):
            ip = config.proxy.server_ip
            if ip:
                addr = '%s,%d' % (ip, config.proxy.server_port)
                asyncio.ensure_future(
                    self.set(
                        proxy_id,
                        sign_proxy_data(addr)
                        )
                    ).add_done_callback(set_key_done)
            else:
                asyncio.ensure_future(
                    self.protocol.stun(
                        boot_nodes[0]
                        )
                    ).add_done_callback(stun_done)

        def listen_done(_):
            asyncio.ensure_future(
                self.bootstrap(
                    boot_nodes
                    )
                ).add_done_callback(bootstrap_done)

        self.listen(port).addCallback(listen_done)

        return d

    def get_peer(self, proxy_id):

        boot_nodes = []
        nodes = (config.proxy.boot_nodes.split())
        for node in nodes:
            addr, port = node.split(':')
            boot_nodes.append((str(addr), int(port)))

        d = defer.Deferred()

        def get_key_done(future):
            value = future.result()
            self.stop()
            if value:
                addr = derive_proxy_data(value)
                d.callback(tuple(addr.split(',')))
            else:
                d.callback(None)

        def bootstrap_done(_):
            asyncio.ensure_future(
                self.get(proxy_id)
                ).add_done_callback(get_key_done)

        def listen_done(_):
            asyncio.ensure_future(
                self.bootstrap(
                    boot_nodes
                    )
                ).add_done_callback(bootstrap_done)

        port = config.proxy.server_kad_port + 2
        self.listen(port).addCallback(listen_done)

        return d
