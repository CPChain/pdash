from twisted.test import proto_helpers
from twisted.trial import unittest

from twisted.internet.defer import Deferred
from twisted.internet import reactor
from cpchain.proxy.server import SSLServerFactory
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.crypto import ECCipher
from cpchain.proxy.proxy_db import Trade, ProxyDB
from cpchain import config

import os, time

def fake_message(test_type):
    buyer_private_key = b'\xa6\xf8_\xee\x1c\x85\xc5\x95\x8d@\x9e\xfa\x80\x7f\xb6\xe0\xb4u\x12\xb6\xdf\x00\xda4\x98\x8e\xaeR\x89~\xf6\xb5'
    buyer_public_key = b'0V0\x10\x06\x07*\x86H\xce=\x02\x01\x06\x05+\x81\x04\x00\n\x03B\x00\x04\\\xfd\xf7\xccD(\x1e\xce`|\x85\xad\xbc*,\x17h.Gj[_N\xadTa\xa9*\xa0x\xff\xb4as\xd1\x94\x9fN\xa3\xe2\xd1fX\xf6\xcf\x8e\xb9+\xab\x0f3\x81\x12\x91\xbdy\xbd\xec\xa6\rZ\x05:\x80'

    seller_private_key = b'\xa6\xf8_\xee\x1c\x85\xc5\x95\x8d@\x9e\xfa\x80\x7f\xb6\xe0\xb4u\x12\xb6\xdf\x00\xda4\x98\x8e\xaeR\x89~\xf6\xb5'
    seller_public_key = b'0V0\x10\x06\x07*\x86H\xce=\x02\x01\x06\x05+\x81\x04\x00\n\x03B\x00\x04\\\xfd\xf7\xccD(\x1e\xce`|\x85\xad\xbc*,\x17h.Gj[_N\xadTa\xa9*\xa0x\xff\xb4as\xd1\x94\x9fN\xa3\xe2\xd1fX\xf6\xcf\x8e\xb9+\xab\x0f3\x81\x12\x91\xbdy\xbd\xec\xa6\rZ\x05:\x80'

    if test_type == 'seller_data':
        message = Message()
        seller_data = message.seller_data
        message.type = Message.SELLER_DATA
        seller_data.order_id = 1
        seller_data.seller_addr = seller_public_key
        seller_data.buyer_addr = buyer_public_key
        seller_data.market_hash = b'MARKET_HASH'
        seller_data.AES_key = b'AES_key'
        storage = seller_data.storage
        storage.type = Message.Storage.IPFS
        ipfs = storage.ipfs
        ipfs.file_hash = b'QmT4kFS5gxzQZJwiDJQ66JLVGPpyTCF912bywYkpgyaPsD'
        ipfs.gateway = "192.168.0.132:5001"

    elif test_type == 'buyer_data':
        message = Message()
        buyer_data = message.buyer_data
        message.type = Message.BUYER_DATA
        buyer_data.order_id = 1
        buyer_data.seller_addr = seller_public_key
        buyer_data.buyer_addr = buyer_public_key
        buyer_data.market_hash = b'MARKET_HASH'

    else:
        message = Message()

    return message

def generate_sign_message(message):
    private_key = b'\xa6\xf8_\xee\x1c\x85\xc5\x95\x8d@\x9e\xfa\x80\x7f\xb6\xe0\xb4u\x12\xb6\xdf\x00\xda4\x98\x8e\xaeR\x89~\xf6\xb5'
    public_key = b'0V0\x10\x06\x07*\x86H\xce=\x02\x01\x06\x05+\x81\x04\x00\n\x03B\x00\x04\\\xfd\xf7\xccD(\x1e\xce`|\x85\xad\xbc*,\x17h.Gj[_N\xadTa\xa9*\xa0x\xff\xb4as\xd1\x94\x9fN\xa3\xe2\xd1fX\xf6\xcf\x8e\xb9+\xab\x0f3\x81\x12\x91\xbdy\xbd\xec\xa6\rZ\x05:\x80'

    sign_message = SignMessage()
    sign_message.public_key = public_key
    sign_message.data = message.SerializeToString()
    sign_message.signature = ECCipher.generate_signature(
                                private_key,
                                sign_message.data
                            )

    return sign_message


def proxy_reply_success(self):
        trade = self.trade
        message = Message()
        message.type = Message.PROXY_REPLY
        proxy_reply = message.proxy_reply
        proxy_reply.AES_key = trade.AES_key
        proxy_reply.file_uuid = trade.file_uuid

        string = message.SerializeToString()
        self.sendString(string)


clean_up = False
class SSLServerTestCase(unittest.TestCase):

    def clean_up_old_data(self, ):
        global clean_up
        if not clean_up:
            clean_up = True
            # init database
            db_path = os.path.join(config.home, config.proxy.dbpath)
            db_path = os.path.expanduser(db_path)
            if os.path.isfile(db_path):
                os.remove(db_path)

            # clean server_root
            server_root = os.path.join(config.home, config.proxy.server_root)
            server_root = os.path.expanduser(server_root)
            for root, dirs, files in os.walk(server_root, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

    def setUp(self):
        self.factory = SSLServerFactory()
        self.clean_up_old_data()

        self.factory.proxy_db = ProxyDB()
        self.factory.proxy_db.session_create()

        self.proto = self.factory.buildProtocol(("localhost", 0))
        self.transport = proto_helpers.StringTransport()
        self.proto.makeConnection(self.transport)

    def defer_task(self, reply_error):
        d = Deferred()
        reactor.callLater(5, d.callback, reply_error)

        return d

    def check_response(self, reply_error):
        string = self.transport.value()
        len, string = string.split(b':')
        message = Message()
        message.ParseFromString(string)

        assert message.type == Message.PROXY_REPLY

        proxy_reply = message.proxy_reply

        if not proxy_reply.error:
            self.assertEqual(proxy_reply.AES_key, b'AES_key')
        else:
            self.assertEqual(reply_error, proxy_reply.error)

    def test_1_buyer_request(self):
        message = fake_message('buyer_data')
        sign_message = generate_sign_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        d = self.defer_task('trade record not found in database')
        d.addCallback(self.check_response)
        return d

    def test_2_seller_request(self):
        message = fake_message('seller_data')
        sign_message = generate_sign_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        d = self.defer_task('')
        d.addCallback(self.check_response)
        return d

    def test_3_seller_request(self):
        message = fake_message('seller_data')
        sign_message = generate_sign_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        d = self.defer_task('trade record already in database')
        d.addCallback(self.check_response)
        return d

    def test_3_sold_to_another_buyer(self):
        message = fake_message('seller_data')
        message.seller_data.buyer_addr = b'fake addr'
        sign_message = generate_sign_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        d = self.defer_task('')
        d.addCallback(self.check_response)
        return d

    def test_4_buyer_request(self):
        message = fake_message('buyer_data')
        sign_message = generate_sign_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        d = self.defer_task('')
        d.addCallback(self.check_response)
        return d

    def test_invalid_signature(self):
        message = fake_message('seller_data')
        sign_message = generate_sign_message(message)
        sign_message.public_key = b'invalid key'
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        d = self.defer_task('wrong signature')
        d.addCallback(self.check_response)
        return d

    def test_S3_storage(self):
        message = fake_message('seller_data')
        message.seller_data.storage.type = Message.Storage.S3
        message.seller_data.storage.s3.uri = 's3 uri'
        sign_message = generate_sign_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        d = self.defer_task('not support S3 storage yet')
        d.addCallback(self.check_response)
        return d

    def test_not_seller_signature(self):
        message = fake_message('seller_data')
        message.seller_data.seller_addr = b'fake addr'
        sign_message = generate_sign_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        d = self.defer_task("not seller's signature")
        d.addCallback(self.check_response)
        return d

    def test_not_buyer_signature(self):
        message = fake_message('buyer_data')
        message.seller_data.seller_addr = b'fake addr'
        sign_message = generate_sign_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        d = self.defer_task("not buyer's signature")
        d.addCallback(self.check_response)
        return d

    def test_invalid_request(self):
        message = fake_message('invalid_data')
        sign_message = generate_sign_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        d = self.defer_task('wrong client request')
        d.addCallback(self.check_response)
        return d
