import logging
import time
import operator

from uuid import uuid1 as uuid

import socket

from twisted.internet import reactor, protocol, defer

import msgpack

from cpchain.proxy.account import sign_proxy_data, derive_proxy_data
from cpchain.proxy.sysconf import get_cpu_info, get_mem_info, get_nic_info, search_peer

logger = logging.getLogger(__name__)

def generate_tid():
    return str(uuid())


class PeerProtocol(protocol.DatagramProtocol): # pylint: disable=too-many-instance-attributes
    def __init__(self, peer_ip=None, peer_id=None, peer_info=None, timeout=5):
        self.timeout = timeout
        self.peer_ip = peer_ip
        self.peer_id = peer_id
        self.peer_info = peer_info
        self.peer_conf = {}
        self.request = {}

        self.peers = {}
        self.peers_lat = {}
        self.peers_conf = {}

    def tranaction_timeout(self, tid):
        self.request[tid][0].callback((False, tid))
        del self.request[tid]

    def send_msg(self, msg, addr):
        try:
            if msg['type']:
                pass
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
                pass
        except:
            logger.debug("receive wrong message %s from %s" % (str(msg), str(addr)))
            return

        if msg['type'] == 'bootstrap':
            tid = msg['tid']
            sign_tid = msg['sign_tid']

            if tid != derive_proxy_data(sign_tid):
                error = 'wrong signature'
                logger.debug(error)
                response = {
                    'type': 'response',
                    'tid': tid,
                    'data': error
                }

            else:
                peer_ip = (msg['peer_ip'] or addr[0], addr[1])
                peer_id = msg['peer_id']
                peer_info = msg['peer_info']
                peer_conf = msg['peer_conf']

                peer = {
                    'addr': peer_ip,
                    'peer_info': peer_info,
                    'ts': time.time()
                }

                self.peers[peer_id] = peer
                self.peers_lat[peer_id] = 0  # initialize
                self.peers_conf[peer_id] = peer_conf

                response = {
                    'type': 'response',
                    'tid': tid,
                    'data': "bootstrap"
                }
                logger.debug("add peer %s at %s" % (peer_id, str(peer['addr'])))

            self.send_msg(response, addr)

        elif msg['type'] == 'ping':
            tid = msg['tid']

            response = {
                'type': 'response',
                'tid': tid,
                'data': 'pong'
            }
            self.send_msg(response, addr)

        elif msg['type'] == 'pick_peer':
            tid = msg['tid']
            sysconf = msg['sysconf']

            pick_peer = None

            if sysconf:
                pick_peer = search_peer(sysconf, self.peers_conf)
            elif self.peers_lat:
                peer_id = min(self.peers_lat.items(), key=operator.itemgetter(1))[0]
                peer = self.peers[peer_id]
                pick_peer = peer_id

            response = {
                'type': 'response',
                'tid': tid,
                'data': pick_peer
            }

            logger.debug("pick peer %s to %s" % (pick_peer, str(addr)))
            self.send_msg(response, addr)

        elif msg['type'] == 'get_peer':
            tid = msg['tid']
            peer_id = msg['peer_id']

            pick_peer = None
            if peer_id in self.peers:
                peer = self.peers[peer_id]
                pick_peer = (peer['addr'][0], peer['peer_info'])

            response = {
                'type': 'response',
                'tid': tid,
                'data': pick_peer
            }

            logger.debug("get peer %s at %s for %s" % \
                            (peer_id, str(pick_peer), str(addr)))
            self.send_msg(response, addr)

        elif msg['type'] == 'response':
            tid = msg['tid']
            data = msg['data']
            self.accept_response(tid, data)

        else:
            logger.debug("receive wrong message %s from %s" % (str(msg), str(addr)))

    def accept_response(self, tid, data):
        d, timeout = self.request[tid]
        timeout.cancel()
        d.callback((True, data))
        del self.request[tid]

    def pick_peer(self, addr, sysconf=None):
        msg = {
            'type': 'pick_peer',
            'tid': generate_tid(),
            'sysconf': sysconf
        }

        return self.send_msg(msg, addr)

    def get_peer(self, peer_id, addr):
        msg = {
            'type': 'get_peer',
            'peer_id': peer_id,
            'tid': generate_tid()
        }

        return self.send_msg(msg, addr)


    def bootstrap(self, addr):
        if self.transport is None:
            return reactor.callLater(1, self.bootstrap)

        self.peer_conf['cpu'] = get_cpu_info()
        self.peer_conf['mem'] = get_mem_info()
        self.peer_conf['nic'] = get_nic_info(addr[0])

        tid = generate_tid()
        msg = {
            'type': 'bootstrap',
            'tid': tid,
            'sign_tid': sign_proxy_data(tid),
            'peer_ip': self.peer_ip,
            'peer_id': self.peer_id,
            'peer_info': self.peer_info,
            'peer_conf': self.peer_conf
            }

        return self.send_msg(msg, addr)


    def ping(self, addr):
        msg = {
            'type': 'ping',
            'tid': generate_tid()
            }

        return self.send_msg(msg, addr)


    def refresh_peers(self):
        now = time.time()
        expired_peers = []

        def refresh(result, peer_id, last):
            success, _ = result

            if success:
                now = time.time()
                self.peers[peer_id]['ts'] = now
                lat = now - last
                self.peers_lat[peer_id] = lat
            return result

        for peer_id in self.peers:
            peer = self.peers[peer_id]
            ts = peer['ts']
            if now - ts > 10:
                expired_peers.append(peer_id)
                logger.debug('retire peer %s' %  str(peer['addr']))
            else:
                addr = peer['addr']
                self.ping(addr).addCallback(refresh, peer_id, time.time())

        for peer in expired_peers:
            self.peers.pop(peer)
