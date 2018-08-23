import time

from twisted.trial import unittest
from twisted.test import proto_helpers

import msgpack

from cpchain.proxy.centralnet import PeerProtocol

peer_id = 'fake_peer_id'

def fake_bootstrap():
    msg = {
        'type': 'bootstrap',
        'tid': 'fake_tid',
        'peer_id': peer_id,
        }

    return msg

def fake_ping():
    msg = {
        'type': 'ping',
        'tid': 'fake_tid',
    }

    return msg

def fake_pick_peer():
    msg = {
        'type': 'pick_peer',
        'tid': 'fake_tid',
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
        self.assertEqual(msg['response'], 'ok')

    def test_ping(self):
        msg = fake_ping()
        data = msgpack.packb(msg, use_bin_type=True)
        self.protocol.datagramReceived(data, self.peer_addr)
        data, addr = self.transport.written[0]
        msg = msgpack.unpackb(data, raw=False)
        self.assertEqual(addr, self.peer_addr)
        self.assertEqual(msg['type'], 'response')
        self.assertEqual(msg['response'], 'ok')

    def test_pick_peer(self):

        self.protocol.peers[peer_id] = self.peer_addr

        msg = fake_pick_peer()
        data = msgpack.packb(msg, use_bin_type=True)
        self.protocol.datagramReceived(data, self.peer_addr)
        data, addr = self.transport.written[0]
        msg = msgpack.unpackb(data, raw=False)
        self.assertEqual(addr, self.peer_addr)
        self.assertEqual(msg['type'], 'response')
        self.assertEqual(msg['response'], peer_id)
