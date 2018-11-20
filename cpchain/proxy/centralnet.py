import logging
import time

from hashlib import sha1
from random import randint

import socket

from twisted.internet.task import LoopingCall

from twisted.internet import protocol, defer

import msgpack

from cpchain.utils import config
from cpchain.utils import reactor
from cpchain.proxy.account import get_proxy_id

logger = logging.getLogger(__name__)

def entropy(length):
    return "".join(chr(randint(0, 255)) for _ in range(length))

def generate_tid():
    h = sha1()
    h.update(entropy(20).encode('utf-8'))
    return h.digest()

class PeerProtocol(protocol.DatagramProtocol):
    def __init__(self):
        self.request = {}
        self.peers = {}
        self.ping_timeouts = {}

    def send_msg(self, msg, addr):
        try:
            if msg['type']:
                tid = msg['tid']
                pack_msg = msgpack.packb(msg, use_bin_type=True)
        except:
            logger.debug("wrong message format sent to %s" % str(addr))
            return

        future = time.time() + 5
        while time.time() < future:
            try:
                self.transport.write(pack_msg, addr)
                break
            except socket.error as e:
                if e.errno in (11, 10055):
                    time.sleep(0.001)
                else:
                    raise socket.error(e)

        if msg['type'] == 'response':
            return

        # for request only
        return self.add_request_callback(tid)

    def add_request_callback(self, tid):

        def tranaction_timeout(tid):
            self.request[tid][0].callback(None)
            del self.request[tid]

        d = defer.Deferred()
        timeout = reactor.callLater(
            5,
            tranaction_timeout,
            tid)

        self.request[tid] = (d, timeout)
        return d

    def trigger_request_callback(self, tid, response):
        d, timeout = self.request[tid]
        timeout.cancel()
        d.callback(response)
        del self.request[tid]

    def bootstrap(self, peer_id, addr):
        if self.transport is None:
            return reactor.callLater(1, self.bootstrap)

        msg = {
            'type': 'bootstrap',
            'tid': generate_tid(),
            'peer_id': peer_id
            }

        return self.send_msg(msg, addr)

    def ping(self, addr):
        msg = {
            'type': 'ping',
            'tid': generate_tid()
            }

        return self.send_msg(msg, addr)

    def pick_peer(self, addr):
        msg = {
            'type': 'pick_peer',
            'tid': generate_tid(),
        }

        return self.send_msg(msg, addr)

    def datagramReceived(self, msg, addr):

        try:
            msg = msgpack.unpackb(msg, raw=False)
            if msg['type']:
                tid = msg['tid']
        except:
            logger.debug("wrong message format received from %s" % str(addr))
            return

        if msg['type'] == 'bootstrap':

            peer_id = msg['peer_id']

            self.peers[peer_id] = addr
            self.ping_timeouts[peer_id] = 0

            response = {
                'type': 'response',
                'tid': tid,
                'response': "ok"
            }

            logger.debug("add peer %s at %s" % (peer_id, str(addr)))

            self.send_msg(response, addr)

        elif msg['type'] == 'ping':

            response = {
                'type': 'response',
                'tid': tid,
                'response': 'ok'
            }
            self.send_msg(response, addr)

        elif msg['type'] == 'pick_peer':

            peer_list = list(self.peers)
            response = {
                'type': 'response',
                'tid': tid,
                'response': peer_list
            }

            logger.debug("pick peer %s to %s" % (str(peer_list), str(addr)))
            self.send_msg(response, addr)

        elif msg['type'] == 'response':
            tid = msg['tid']
            response = msg['response']
            self.trigger_request_callback(tid, response)

        else:
            logger.error("wrong message received from %s" % str(addr))

    def refresh_peers(self):

        def ping_response(response, peer_id):
            if response is None:
                if self.ping_timeouts[peer_id] == 5:
                    logger.debug("remove peer %s at %s" % (peer_id, str(self.peers[peer_id])))
                    del self.peers[peer_id]
                    del self.ping_timeouts[peer_id]
                else:
                    self.ping_timeouts[peer_id] += 1

        for peer_id in self.peers:
            addr = self.peers[peer_id]
            self.ping(addr).addCallback(ping_response, peer_id)

class Tracker:
    protocol = PeerProtocol()

    def run(self):
        _, port = config.proxy.tracker.split(':')
        port = int(port)
        self.trans = reactor.listenUDP(port, self.protocol)
        self.refresh_loop = LoopingCall(self.protocol.refresh_peers).start(60)

    def stop(self):
        self.refresh_loop.cancel()
        self.trans.stopListening()

class Slave:
    def __init__(self):
        self.protocol = PeerProtocol()
        host, port = config.proxy.tracker.split(':')
        port = int(port)
        self.tracker = (host, port)

    def run(self):
        port = config.proxy.server_slave_port
        self.trans = reactor.listenUDP(port, self.protocol)
        return self.protocol.bootstrap(get_proxy_id(), self.tracker)

    def stop(self):
        self.trans.stopListening()

    def pick_peer(self, port=None):
        port = port or config.proxy.server_slave_port + 2
        self.trans = reactor.listenUDP(port, self.protocol)

        def stop_listening(response):
            self.stop()
            return response

        d = self.protocol.pick_peer(self.tracker).addCallback(stop_listening)

        return d
