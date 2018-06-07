import time

from twisted.trial import unittest
from twisted.test import proto_helpers

import msgpack

from cpchain.proxy.network import PeerProtocol, generate_tid
from cpchain.proxy.account import set_proxy_account, get_proxy_id, sign_proxy_data

set_proxy_account()
peer_id = get_proxy_id()
service_port = 5678

def fake_bootstrap():
    tid = generate_tid()
    msg = {
        'type': 'bootstrap',
        'tid': tid,
        'sign_tid': sign_proxy_data(tid),
        'peer_ip': None,
        'peer_id': peer_id,
        'peer_info': service_port,
        'peer_conf': None
        }

    return msg

def fake_pick_peer():
    msg = {
        'type': 'pick_peer',
        'tid': generate_tid(),
        'sysconf': None
    }

    return msg

def fake_get_peer():
    msg = {
        'type': 'get_peer',
        'peer_id': peer_id,
        'tid': generate_tid()
    }

    return msg


class PeerProtocolTest(unittest.TestCase):
    def setUp(self):
        self.protocol = PeerProtocol()
        self.transport = proto_helpers.FakeDatagramTransport()
        self.protocol.transport = self.transport
        self.protocol.startProtocol()
        self.peer_addr = ('127.0.0.1', 8100)

    def test_bootstrap(self):
        msg = fake_bootstrap()
        data = msgpack.packb(msg, use_bin_type=True)
        self.protocol.datagramReceived(data, self.peer_addr)
        data, addr = self.transport.written[0]
        msg = msgpack.unpackb(data, raw=False)
        self.assertEqual(addr, self.peer_addr)
        self.assertEqual(msg['type'], 'response')
        self.assertEqual(msg['data'], 'bootstrap')
        self.assertEqual(
            self.protocol.peers[peer_id]['addr'],
            self.peer_addr)

    def test_pick_peer(self):
        peer = {
            'addr': self.peer_addr,
            'peer_info': service_port,
            'ts': time.time()
            }

        self.protocol.peers[peer_id] = peer
        self.protocol.peers_lat[peer_id] = 1

        msg = fake_pick_peer()
        data = msgpack.packb(msg, use_bin_type=True)
        self.protocol.datagramReceived(data, self.peer_addr)
        data, addr = self.transport.written[0]
        msg = msgpack.unpackb(data, raw=False)
        self.assertEqual(addr, self.peer_addr)
        self.assertEqual(msg['type'], 'response')
        self.assertEqual(msg['data'], peer_id)

    def test_get_peer(self):
        peer = {
            'addr': self.peer_addr,
            'peer_info': service_port,
            'ts': time.time()
            }

        self.protocol.peers[peer_id] = peer

        msg = fake_get_peer()
        data = msgpack.packb(msg, use_bin_type=True)
        self.protocol.datagramReceived(data, self.peer_addr)
        data, addr = self.transport.written[0]
        msg = msgpack.unpackb(data, raw=False)
        self.assertEqual(addr, self.peer_addr)
        self.assertEqual(msg['type'], 'response')
        self.assertEqual(msg['data'][0], self.peer_addr[0])
        self.assertEqual(msg['data'][1], service_port)
