import logging
import time

from hashlib import sha1
from random import randint

import socket

from twisted.internet import reactor, protocol, defer

import msgpack

logger = logging.getLogger(__name__)

def entropy(length):
    return "".join(chr(randint(0, 255)) for _ in range(length))

def generate_tid():
    return entropy(20)

def generate_peer_id():
    h = sha1()
    h.update(entropy(20).encode('utf-8'))
    return h.digest()

class PeerProtocol(protocol.DatagramProtocol):
    def __init__(self, peer_info=None, timeout=5):
        self.peer_id = generate_peer_id()
        self.addr = None
        self.peers = {}
        self.request = {}
        self.timeout = timeout
        self.peer_info = peer_info
        self.peer_stat = None

    def tranaction_timeout(self, tid):
        self.request[tid][0].callback((False, tid))
        del self.request[tid]

    def send_msg(self, msg, addr):
        try:
            if msg['type']:
                logger.debug('send %s to %s' %  (str(msg['type']), str(addr)))
        except:
            logger.debug("send wrong message %s to %s" % (str(msg), str(addr)))
            return

        tid = msg['tid']
        data = msgpack.packb(msg, use_bin_type=True)
        future = time.time() + self.timeout
        while time.time() < future:
            try:
                self.transport.write(data, addr)
                break
            except socket.error as e:
                if e.errno in (11, 10055):
                    time.sleep(0.001)
                else:
                    raise socket.error(e)

        if msg['type'] == 'response':
            return

        # for request only
        d = defer.Deferred()
        timeout = reactor.callLater(self.timeout,
                                    self.tranaction_timeout, tid)
        self.request[tid] = (d, timeout)
        d.addBoth(self.dummy_callback)
        return d

    def dummy_callback(self, result):
        return result

    def datagramReceived(self, data, addr):
        msg = msgpack.unpackb(data, raw=False)

        try:
            if msg['type']:
                logger.debug('receive %s from %s' %  (str(msg['type']), str(addr)))
        except:
            logger.debug("receive wrong message %s from %s" % (str(msg), str(addr)))
            return


        if msg['type'] == 'bootstrap':
            peer_id = msg['peer_id']
            tid = msg['tid']
            peer_info = msg['peer_info']
            peer_stat = msg['peer_stat']

            if peer_id in self.peers:
                logger.debug("duplicate bootstrap message")
            else:
                # welcome new peer
                peer = {
                    'addr': addr,
                    'peer_info': peer_info,
                    'ts': time.time(),
                    'peer_stat': peer_stat
                }

                self.peers[peer_id] = peer
                logger.debug("add peer %s" % str(peer['addr']))

            response = {
                'type': 'response',
                'tid': tid,
                'data': "bootstrap"
            }
            self.send_msg(response, addr)

        elif msg['type'] == 'ping':
            tid = msg['tid']

            response = {
                'type': 'response',
                'tid': tid,
                'data': 'pong'
            }
            self.send_msg(response, addr)

        elif msg['type'] == 'select_peer':
            tid = msg['tid']

            bootnode_addr = tuple(msg['bootnode_addr'])
            logger.debug("boot node addr: %s" % str(bootnode_addr))

            # could select boot node itself
            select_peer_stat = self.peer_stat
            select_peer = (bootnode_addr[0], self.peer_info)

            for peer_id in self.peers:
                peer = self.peers[peer_id]
                peer_stat = peer['peer_stat']
                if peer_stat < select_peer_stat:
                    select_peer_stat = peer_stat
                    select_peer = (peer['addr'][0], peer['peer_info'])

            response = {
                'type': 'response',
                'tid': tid,
                'data': select_peer
            }

            self.send_msg(response, addr)

        elif msg['type'] == 'response':
            tid = msg['tid']
            data = msg['data']
            self.accept_response(tid, data)

    def accept_response(self, tid, data):
        d, timeout = self.request[tid]
        timeout.cancel()
        d.callback((True, data))
        del self.request[tid]

    def select_peer(self, addr):
        msg = {
            'type': 'select_peer',
            'tid': generate_tid(),
            'bootnode_addr': addr
        }

        return self.send_msg(msg, addr)

    def bootstrap(self, addr):
        msg = {
            'type': 'bootstrap',
            'tid': generate_tid(),
            'peer_id': self.peer_id,
            'peer_info': self.peer_info,
            'peer_stat': self.peer_stat
            }

        return self.send_msg(msg, addr)


    def ping(self, addr):
        msg = {
            'type': 'ping',
            'tid': generate_tid()
            }

        return self.send_msg(msg, addr)

    def refresh_peer(self, result, peer):
        success, data = result
        if success:
            peer['ts'] = time.time()
        return result

    def refresh_peers(self):
        now = time.time()
        expired_peers = []
        for peer_id in self.peers:
            peer = self.peers[peer_id]
            ts = peer['ts']
            if now - ts > 10:
                expired_peers.append(peer_id)
                logger.debug('retire peer %s' %  str(peer['addr']))
            else:
                addr = peer['addr']
                self.ping(addr).addCallback(self.refresh_peer, peer)

        for peer in expired_peers:
            self.peers.pop(peer)
