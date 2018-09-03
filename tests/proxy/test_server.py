# run trial test with following command:
#     python3 -m twisted.trial ./test_server.py

import os

from twisted.test import proto_helpers
from twisted.trial import unittest
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Factory

from cpchain.utils import reactor, join_with_rc

from cpchain.account import Accounts
from cpchain.crypto import ECCipher

from cpchain.proxy import chain
chain.order_is_ready_on_chain = lambda _: True
chain.claim_data_fetched_to_chain = lambda _: True
chain.claim_data_delivered_to_chain = lambda _: True

from cpchain.proxy.server import SSLServerProtocol
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.db import ProxyDB
from cpchain import config

accounts = Accounts()
buyer_account = accounts[0]
seller_account = accounts[1]

buyer_private_key = buyer_account.private_key  #object type
buyer_public_key = ECCipher.serialize_public_key(
    buyer_account.public_key)    # string type
buyer_addr = ECCipher.get_address_from_public_key(
    buyer_account.public_key)  #string type

seller_private_key = seller_account.private_key
seller_public_key = ECCipher.serialize_public_key(
    seller_account.public_key)   #string type
seller_addr = ECCipher.get_address_from_public_key(
    seller_account.public_key)  #string type

order_id = 1
order_type = 'file'

def fake_seller_message():
    message = Message()
    seller_data = message.seller_data
    message.type = Message.SELLER_DATA
    seller_data.order_id = order_id
    seller_data.order_type = order_type
    seller_data.seller_addr = seller_addr
    seller_data.buyer_addr = buyer_addr
    seller_data.market_hash = 'MARKET_HASH'
    seller_data.AES_key = b'AES_key'
    storage = seller_data.storage
    storage.type = 'template'
    storage.file_uri = 'fake_file_uri'

    return message

def fake_buyer_message():
    message = Message()
    buyer_data = message.buyer_data
    message.type = Message.BUYER_DATA
    buyer_data.order_id = order_id
    buyer_data.order_type = order_type
    buyer_data.seller_addr = seller_addr
    buyer_data.buyer_addr = buyer_addr
    buyer_data.market_hash = 'MARKET_HASH'

    return message

def sign_seller_message(message):
    sign_message = SignMessage()
    sign_message.public_key = seller_public_key
    sign_message.data = message.SerializeToString()
    sign_message.signature = ECCipher.create_signature(
        seller_private_key,
        sign_message.data
        )

    return sign_message

def sign_buyer_message(message):
    sign_message = SignMessage()
    sign_message.public_key = buyer_public_key
    sign_message.data = message.SerializeToString()
    sign_message.signature = ECCipher.create_signature(
        buyer_private_key,
        sign_message.data
        )

    return sign_message


_clean_up_db = False
class SSLServerTestCase(unittest.TestCase):

    def clean_up_old_data(self, ):
        global _clean_up_db  # pylint: disable=global-statement
        if not _clean_up_db:
            _clean_up_db = True
            # init database
            db_path = join_with_rc(config.proxy.dbpath)
            if os.path.isfile(db_path):
                os.remove(db_path)

            # clean server_root
            server_root = join_with_rc(config.proxy.server_root)
            for root, dirs, files in os.walk(server_root, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

    def setUp(self):
        self.factory = Factory()
        self.factory.protocol = SSLServerProtocol
        self.clean_up_old_data()

        self.proto = self.factory.buildProtocol(("localhost", 0))

        self.proto.proxy_db = ProxyDB()
        self.proto.port_conf = {
            'file': config.proxy.server_file_port,
            'stream_ws': config.proxy.server_stream_ws_port,
            'stream_restful': config.proxy.server_stream_restful_port
        }

        self.transport = proto_helpers.StringTransport()
        self.proto.makeConnection(self.transport)

    def check_response_later(self, reply_error, wait=1):
        d = Deferred()
        reactor.callLater(wait, d.callback, reply_error)
        d.addCallback(self.check_response)

        return d

    def check_response(self, reply_error):
        string = self.transport.value()
        _, string = string.split(b':', 1)

        message = Message()
        message.ParseFromString(string)

        assert message.type == Message.PROXY_REPLY

        proxy_reply = message.proxy_reply

        if not proxy_reply.error:
            self.assertEqual(proxy_reply.AES_key, b'AES_key')
        else:
            self.assertEqual(reply_error, proxy_reply.error)

    def test_1_buyer_request(self):
        message = fake_buyer_message()
        sign_message = sign_buyer_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        return self.check_response_later('trade record not found in database')

    def test_2_seller_request(self):
        message = fake_seller_message()
        sign_message = sign_seller_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        return self.check_response_later('')

    def test_3_seller_request(self):
        message = fake_seller_message()
        sign_message = sign_seller_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        return self.check_response_later('trade record already in database')

    def test_3_sold_to_another_buyer(self):
        message = fake_seller_message()
        message.seller_data.order_id = 2
        message.seller_data.buyer_addr = b'fake addr'
        sign_message = sign_seller_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        return self.check_response_later('')

    def test_4_buyer_request(self):
        message = fake_buyer_message()
        sign_message = sign_buyer_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        return self.check_response_later('')

    def test_invalid_signature(self):
        message = fake_buyer_message()
        sign_message = sign_buyer_message(message)
        sign_message.public_key = 'invalid key'
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        return self.check_response_later('wrong signature')

    def test_key_not_match_address(self):
        message = fake_buyer_message()
        message.buyer_data.buyer_addr = 'fake addr'
        sign_message = sign_buyer_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        return self.check_response_later('public key does not match with address')

    def test_invalid_request(self):
        message = fake_buyer_message()
        message.type = 3 # any value large than 2 is invalid
        sign_message = sign_buyer_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        return self.check_response_later('wrong client request')
