import logging
import time

from hashlib import sha1
from random import randint

import socket
import msgpack

from twisted.internet import reactor, protocol, defer

from twisted.internet.task import LoopingCall

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

        if msg['type'] == 'ping':
            peer_id = msg['peer_id']
            peer_info = msg['peer_info']
            peer_stat = msg['peer_stat']

            if peer_id in self.peers:
                peer = self.peers[peer_id]
                if addr == peer['addr']:
                    #refresh peer timestamp and statistics
                    logger.debug('refresh peer %s' % str(addr))
                    peer['ts'] = time.time()
                    peer['peer_stat'] = peer_stat
                else:
                    logger.error("something wrong")
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

                self.share_peers(addr)

        elif msg['type'] == 'share_peer':
            peer_id = msg['peer_id']
            peer_info = msg['peer_info']
            peer_stat = msg['peer_stat']

            if peer_id in self.peers:
                # other peer already shared this peer
                peer = self.peers[peer_id]
                logger.debug('known peer %s' % str(peer['addr']))
            else:
                peer = {
                    'addr': tuple(msg['addr']),
                    'peer_info': peer_info,
                    'ts': time.time(),
                    'peer_stat': peer_stat
                }
                self.peers[peer_id] = peer
                logger.debug("add share peer %s" % str(peer['addr']))

        elif msg['type'] == 'select_peer':
            tid = msg['tid']
            logger.debug("select peer request from %s" % str(addr))

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

        logger.debug('ask %s to recommend a peer' % str(addr))
        return self.send_msg(msg, addr)

    def share_peers(self, addr):

        for peer_id in self.peers:
            peer = self.peers[peer_id]
            peer_addr = peer['addr']
            peer_info = peer['peer_info']
            peer_stat = peer['peer_stat']
            msg = {
                'type': 'share_peer',
                'tid': generate_tid(),
                'peer_id': peer_id,
                'peer_info': peer_info,
                'peer_stat': peer_stat,
                'addr': peer_addr
            }

            if addr != peer_addr:
                self.send_msg(msg, addr)
                logger.debug('share peer %s to %s' % \
                        (str(peer_addr), str(addr)))


    def ping(self, addr):
        msg = {
            'type': 'ping',
            'tid': generate_tid(),
            'peer_id': self.peer_id,
            'peer_info': self.peer_info,
            'peer_stat': self.peer_stat
            }

        self.send_msg(msg, addr)
        logger.debug('send ping msg to %s' %  str(addr))

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
                self.ping(addr)

        for peer in expired_peers:
            self.peers.pop(peer)
