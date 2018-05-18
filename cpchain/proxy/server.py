#!/usr/bin/env python3

import os, time
import logging

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from twisted.internet import threads, protocol
from twisted.protocols.basic import NetstringReceiver

from twisted.web.resource import Resource, ForbiddenResource
from twisted.web.static import File

from eth_utils import to_bytes

from cpchain import config
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.message import message_sanity_check, \
sign_message_verify, is_address_from_key
from cpchain.crypto import ECCipher # pylint: disable=no-name-in-module

from cpchain.storage import IPFSStorage
from cpchain.proxy.proxy_db import Trade, ProxyDB
from cpchain.chain.agents import ProxyAgent # pylint: disable=no-name-in-module
from cpchain.chain.utils import default_w3
from cpchain.utils import join_with_root, join_with_rc, Encoder

logger = logging.getLogger(__name__)

server_root = join_with_rc(config.proxy.server_root)
server_root = os.path.expanduser(server_root)
os.makedirs(server_root, exist_ok=True)

class SSLServerProtocol(NetstringReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.proxy_db = factory.proxy_db

        self.peer = None
        self.trade = None

    def connectionMade(self):
        self.factory.numConnections += 1
        self.peer = str(self.transport.getPeer())
        logger.debug("connect to client %s" % self.peer)

    def stringReceived(self, string):
        sign_message = SignMessage()
        sign_message.ParseFromString(string)

        valid = sign_message_verify(sign_message)

        if not valid:
            error = 'wrong signature'
            self.proxy_reply_error(error)
            return

        message = Message()
        message.ParseFromString(sign_message.data)
        valid = message_sanity_check(message)
        if not valid or message.type == Message.PROXY_REPLY:
            error = "wrong client request"
            self.proxy_reply_error(error)
            return

        public_key = sign_message.public_key

        proxy_db = self.proxy_db
        self.trade = Trade()
        trade = self.trade
        error = None

        if message.type == Message.SELLER_DATA:
            data = message.seller_data
            trade.order_id = data.order_id
            trade.seller_addr = data.seller_addr
            trade.buyer_addr = data.buyer_addr
            trade.market_hash = data.market_hash
            trade.AES_key = data.AES_key

            if not is_address_from_key(data.seller_addr, public_key):
                error = "not seller's signature"
                self.proxy_reply_error(error)
                return

            storage = data.storage
            if storage.type == Message.Storage.IPFS:
                ipfs = storage.ipfs
                trade.file_hash = ipfs.file_hash
                if proxy_db.count(trade):
                    error = "trade record already in database"
                    self.proxy_reply_error(error)
                    return
                else:
                    file_path = os.path.join(
                        server_root,
                        trade.file_hash.decode()
                        )

                    # seller sold the same file to another buyer
                    if os.path.isfile(file_path):
                        mtime = time.time()
                        os.utime(file_path, (mtime, mtime))
                        proxy_db.insert(trade)
                        self.proxy_reply_success()

                        self.proxy_claim_relay()

                        return
                    else:
                        d = threads.deferToThread(
                            self.get_ipfs_file,
                            ipfs.gateway,
                            trade.file_hash
                            )

                        d.addBoth(self.ipfs_callback)

            elif storage.type == Message.Storage.S3:
                error = "not support S3 storage yet"
                self.proxy_reply_error(error)
                return

        elif message.type == Message.BUYER_DATA:
            data = message.buyer_data
            trade.order_id = data.order_id
            trade.seller_addr = data.seller_addr
            trade.buyer_addr = data.buyer_addr
            trade.market_hash = data.market_hash

            if not is_address_from_key(data.buyer_addr, public_key):
                error = "not buyer's signature"
                self.proxy_reply_error(error)
                return

            if proxy_db.count(trade):
                self.trade = proxy_db.query(trade)
                self.proxy_reply_success()
            else:
                error = "trade record not found in database"
                self.proxy_reply_error(error)

    def proxy_claim_relay(self):
        proxy_trans = ProxyAgent(default_w3, config.chain.core_contract)
        private_key_file_path = join_with_root(config.wallet.private_key_file)
        password_path = join_with_root(config.wallet.private_key_password_file)
        with open(password_path) as f:
            password = f.read()
        priv_key, _ = ECCipher.load_key_pair_from_keystore(private_key_file_path, password)
        priv_key_bytes = Encoder.str_to_base64_byte(priv_key)
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(ECCipher.generate_signature(priv_key_bytes, to_bytes(self.trade.order_id)))
        deliver_hash = digest.finalize()
        tx_hash = proxy_trans.claim_relay(self.trade.order_id, deliver_hash)
        return tx_hash

    def proxy_reply_success(self):
        trade = self.trade
        message = Message()
        message.type = Message.PROXY_REPLY
        proxy_reply = message.proxy_reply
        proxy_reply.AES_key = trade.AES_key
        proxy_reply.file_uuid = trade.file_uuid

        string = message.SerializeToString()
        self.sendString(string)
        self.transport.loseConnection()

    def get_ipfs_file(self, ipfs_gateway, file_hash):
        host, port = ipfs_gateway.strip().split(':')
        ipfs = IPFSStorage()
        return ipfs.connect(host, port) and \
                ipfs.download_file(file_hash, server_root)

    def ipfs_callback(self, success):
        if success:
            self.proxy_db.insert(self.trade)
            self.proxy_reply_success()

            self.proxy_claim_relay()
        else:
            error = "failed to get file from ipfs"
            self.proxy_reply_error(error)

    def connectionLost(self, reason):
        self.factory.numConnections -= 1
        logger.debug("lost connection to client %s" % self.peer)

    def proxy_reply_error(self, error):
        message = Message()
        message.type = Message.PROXY_REPLY
        proxy_reply = message.proxy_reply
        proxy_reply.error = error
        string = message.SerializeToString()
        self.sendString(string)
        self.transport.loseConnection()

class SSLServerFactory(protocol.Factory):
    numConnections = 0

    def __init__(self):
        self.proxy_db = None

    def buildProtocol(self, addr):
        return SSLServerProtocol(self)

    def startFactory(self):
        self.proxy_db = ProxyDB()
        self.proxy_db.session_create()

    def stopFactory(self):
        self.proxy_db.session_close()


class FileServer(Resource):

    def __init__(self):
        Resource.__init__(self)
        self.proxy_db = ProxyDB()
        self.proxy_db.session_create()

    def getChild(self, path, request):

        # don't expose the file list under root dir
        # for security consideration
        if path == b'':
            return ForbiddenResource()

        uuid = path.decode()
        trade = Trade()
        trade = self.proxy_db.query_file_uuid(uuid)
        if trade:
            file_hash = trade.file_hash
            file_path = os.path.join(server_root, file_hash.decode())
            return File(file_path)

        return ForbiddenResource()
