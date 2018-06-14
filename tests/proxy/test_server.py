# run trial test with following command:
#     python3 -m twisted.trial ./test_server.py

import os

from twisted.test import proto_helpers
from twisted.trial import unittest
from twisted.internet.defer import Deferred

from cpchain.utils import reactor, join_with_rc

from cpchain.account import Accounts
from cpchain.crypto import ECCipher

from cpchain.proxy import chain
chain.order_is_ready_on_chain = lambda _: True
chain.claim_data_fetched_to_chain = lambda _: True
chain.claim_data_delivered_to_chain = lambda _: True

from cpchain.proxy.server import SSLServerFactory
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.db import ProxyDB
from cpchain import config

from cpchain.storage import IPFSStorage, S3Storage

def mock_ipfs_download_file(_, file_hash, file_dir):
    open(os.path.join(file_dir, file_hash), 'a').close()
    return True

IPFSStorage.connect = lambda *args: True
IPFSStorage.download_file = mock_ipfs_download_file

def mock_s3_download_file(_, fpath, remote_fpath, fsize=None, bucket=None):
    open(fpath, 'a').close()

S3Storage.__init__ = lambda *args: None
S3Storage.download_file = mock_s3_download_file

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


def fake_seller_message(storage_type):
    message = Message()
    seller_data = message.seller_data
    message.type = Message.SELLER_DATA
    seller_data.order_id = 1
    seller_data.seller_addr = seller_addr
    seller_data.buyer_addr = buyer_addr
    seller_data.market_hash = 'MARKET_HASH'
    seller_data.AES_key = b'AES_key'
    storage = seller_data.storage

    if storage_type == 'ipfs':
        storage.type = Message.Storage.IPFS
        ipfs = storage.ipfs
        ipfs.file_hash = 'fake_file_hash'
        ipfs.gateway = "1.2.3.4:5001"

    elif storage_type == 's3':
        storage.type = Message.Storage.S3
        s3 = storage.s3
        s3.bucket = 'fake-bucket'
        s3.key = 'fake-key'

    return message

def fake_buyer_message():
    message = Message()
    buyer_data = message.buyer_data
    message.type = Message.BUYER_DATA
    buyer_data.order_id = 1
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
            db_path = os.path.expanduser(db_path)
            if os.path.isfile(db_path):
                os.remove(db_path)

            # clean server_root
            server_root = join_with_rc(config.proxy.server_root)
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

        self.factory.ip = '127.0.0.1'
        self.factory.data_port = 8001

        self.proto = self.factory.buildProtocol(("localhost", 0))
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
        message = fake_seller_message('ipfs')
        sign_message = sign_seller_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        return self.check_response_later('')

    def test_3_seller_request(self):
        message = fake_seller_message('ipfs')
        sign_message = sign_seller_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        return self.check_response_later('trade record already in database')

    def test_3_sold_to_another_buyer(self):
        message = fake_seller_message('ipfs')
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

    def test_S3_storage(self):
        message = fake_seller_message('s3')
        message.seller_data.order_id = 3
        sign_message = sign_seller_message(message)
        string = sign_message.SerializeToString()
        self.proto.stringReceived(string)
        return self.check_response_later('')

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
