import logging
import sys
import time

from hashlib import sha1
from random import randint

import socket
import umsgpack

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
    def __init__(self, port=None, timeout=5):
        self.peer_id = generate_peer_id()
        self.addr = None
        self.peers = {}
        self.request = {}
        self.timeout = timeout

        self.refresh_loop = LoopingCall(self.refresh_peers)

    def tranaction_timeout(self, tid):
        self.request[tid][0].callback((False, tid))
        del self.request[tid]

    def send_msg(self, msg, addr):
        tid = msg['tid']
        data = umsgpack.packb(msg)
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

    def run(self, port):
        port = port or 5678
        self.refresh_loop.start(5)

        return reactor.listenUDP(port, self)

    def datagramReceived(self, data, addr):
        msg = umsgpack.unpackb(data)

        if msg['type'] == 'ping':
            peer_id = msg['peer_id']

            if peer_id in self.peers:
                peer = self.peers[peer_id]
                if addr == peer['addr']:
                    #refresh peer timestamp
                    logger.info('refresh peer %s' % str(addr))
                    peer['ts'] = time.time()
                else:
                    logger.error("something wrong")
            else:
                # welcome new peer
                peer = {
                    'addr': addr,
                    'ts': time.time()
                }

                self.peers[peer_id] = peer
                logger.debug("add peer %s" % str(peer['addr']))

                self.share_peers(addr)

        elif msg['type'] == 'share_peer':
            peer_id = msg['peer_id']

            if peer_id in self.peers:
                # other peer already shared this peer
                peer = self.peers[peer_id]
                logger.debug('known peer %s' % str(peer['addr']))
            else:
                peer = {
                    'addr': (msg['addr'][0], msg['addr'][1]),
                    'ts': time.time()
                }
                self.peers[peer_id] = peer
                logger.debug("add share peer %s" % str(peer['addr']))

        elif msg['type'] == 'select_peer':
            tid = msg['tid']
            logger.debug('select peer')

            data = []
            for peer_id in self.peers:
                data.append(self.peers[peer_id]['addr'])
            response = {
                'type': 'response',
                'tid': tid,
                'data': data
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
        }

        logger.debug('ask %s to recommend a peer' % str(addr))
        return self.send_msg(msg, addr)

    def share_peers(self, addr):

        for peer_id in self.peers:
            peer_addr = self.peers[peer_id]['addr']
            msg = {
                'type': 'share_peer',
                'tid': generate_tid(),
                'peer_id': peer_id,
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



if __name__ == '__main__':
    # for testing purpose
    log_format='%(asctime)s [%(levelname)s]%(funcName)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)


    if sys.argv[1] == 'tracker':
        node = PeerProtocol()
        node.run(5678)

    elif sys.argv[1] == 'peer':
        node = PeerProtocol()
        node.run(4567)
        node.ping(('192.168.0.169', 5678))

    elif sys.argv[1] == 'client':
        node = PeerProtocol()
        node.run(7890)

        def print_node(result):
            success, data = result
            if success:
                print(data)
            reactor.stop()

            node.transport.stopListening()

        node.select_peer(('192.168.0.169', 5678)).addCallback(print_node)

    reactor.run()
