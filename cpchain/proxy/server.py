#!/usr/bin/env python3

import os, time
import logging

# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import hashes

from twisted.internet import threads, protocol
from twisted.protocols.basic import NetstringReceiver

from twisted.web.resource import Resource, ForbiddenResource
from twisted.web.static import File

# from eth_utils import to_bytes

from cpchain import config
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.message import message_sanity_check, \
sign_message_verify, is_address_from_key
# from cpchain.crypto import ECCipher

from cpchain.storage import IPFSStorage, S3Storage
from cpchain.proxy.db import Trade, ProxyDB
# from cpchain.chain.agents import ProxyAgent
# from cpchain.chain.utils import default_w3
# from cpchain.utils import join_with_root, join_with_rc, Encoder
from cpchain.utils import join_with_rc

logger = logging.getLogger(__name__)

server_root = join_with_rc(config.proxy.server_root)
server_root = os.path.expanduser(server_root)
os.makedirs(server_root, exist_ok=True)

class SSLServerProtocol(NetstringReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.proxy_db = factory.proxy_db

        self.peer = None

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
            return self.proxy_reply_error(error)

        message = Message()
        message.ParseFromString(sign_message.data)
        valid = message_sanity_check(message)
        if not valid or message.type == Message.PROXY_REPLY:
            error = "wrong client request"
            return self.proxy_reply_error(error)

        public_key = sign_message.public_key

        if message.type == Message.SELLER_DATA:
            public_addr = message.seller_data.seller_addr
        elif message.type == Message.BUYER_DATA:
            public_addr = message.buyer_data.buyer_addr

        if not is_address_from_key(public_addr, public_key):
            error = "public key does not match with address"
            return self.proxy_reply_error(error)

        self.handle_message(message)

    def handle_message(self, message):

        proxy_db = self.proxy_db
        trade = Trade()

        if message.type == Message.SELLER_DATA:
            data = message.seller_data
            trade.order_id = data.order_id

            if proxy_db.count(trade):
                error = "trade record already in database"
                return self.proxy_reply_error(error)

            trade.seller_addr = data.seller_addr
            trade.buyer_addr = data.buyer_addr
            trade.market_hash = data.market_hash
            trade.AES_key = data.AES_key

            storage = data.storage
            if storage.type == Message.Storage.IPFS:
                ipfs = storage.ipfs
                trade.file_hash = ipfs.file_hash

                file_path = os.path.join(
                    server_root,
                    trade.file_hash.decode()
                    )

                # seller sold the same file to another buyer
                if os.path.isfile(file_path):
                    mtime = time.time()
                    os.utime(file_path, (mtime, mtime))
                    proxy_db.insert(trade)

                    # self.proxy_claim_relay()
                    return self.proxy_reply_success(trade)


                def download_ipfs_file():
                    host, port = ipfs.gateway.strip().split(':')
                    file_hash = trade.file_hash
                    ipfs_storage = IPFSStorage()
                    return ipfs_storage.connect(host, port) and \
                            ipfs_storage.download_file(
                                file_hash, server_root)

                d = threads.deferToThread(
                    download_ipfs_file
                    )

                d.addCallback(self.file_download_finished, trade)

            elif storage.type == Message.Storage.S3:
                s3 = storage.s3
                bucket = s3.bucket
                key = s3.key

                # use order id as the local file name to avoid conflict
                file_name = str(trade.order_id)
                trade.file_hash = file_name.encode('utf-8')
                file_path = os.path.join(server_root, file_name)

                def download_s3_file():
                    try:
                        S3Storage().download_file(
                            fpath=file_path,
                            remote_fpath=key,
                            bucket=bucket
                            )
                    except:
                        logger.exception('failed to download S3 file')
                        return False
                    else:
                        return True

                d = threads.deferToThread(
                    download_s3_file
                )

                d.addCallback(self.file_download_finished, trade)

        elif message.type == Message.BUYER_DATA:
            data = message.buyer_data
            trade.order_id = data.order_id

            if proxy_db.count(trade):
                trade = proxy_db.query(trade)
                self.proxy_reply_success(trade)
            else:
                error = "trade record not found in database"
                self.proxy_reply_error(error)

    def proxy_claim_relay(self):
        pass
        # TODO: Some thing changed since last merge, need to update accordingly
        # proxy_trans = ProxyAgent(default_w3, config.chain.core_contract)
        # private_key_file_path = join_with_root(config.wallet.private_key_file)
        # password_path = join_with_root(config.wallet.private_key_password_file)
        # with open(password_path) as f:
        #     password = f.read()
        # priv_key, _ = ECCipher.load_key_pair_from_keystore(private_key_file_path, password)
        # priv_key_bytes = Encoder.str_to_base64_byte(priv_key)
        # digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        # digest.update(ECCipher.generate_signature(priv_key_bytes, to_bytes(self.trade.order_id)))
        # deliver_hash = digest.finalize()
        # tx_hash = proxy_trans.claim_relay(self.trade.order_id, deliver_hash)
        # return tx_hash

    def file_download_finished(self, success, trade):
        if success:
            self.proxy_db.insert(trade)
            self.proxy_reply_success(trade)
            # self.proxy_claim_relay()
        else:
            error = "failed to download file"
            self.proxy_reply_error(error)

    def proxy_reply_success(self, trade):
        message = Message()
        message.type = Message.PROXY_REPLY
        proxy_reply = message.proxy_reply
        proxy_reply.AES_key = trade.AES_key
        file_uri = "https://%s:%d/%s" % (
            self.factory.ip,
            self.factory.data_port,
            trade.file_uuid)
        proxy_reply.file_uri = file_uri

        string = message.SerializeToString()
        self.sendString(string)
        self.transport.loseConnection()

    def proxy_reply_error(self, error):
        message = Message()
        message.type = Message.PROXY_REPLY
        proxy_reply = message.proxy_reply
        proxy_reply.error = error
        string = message.SerializeToString()
        self.sendString(string)
        self.transport.loseConnection()

    def connectionLost(self, reason):
        self.factory.numConnections -= 1
        logger.debug("lost connection to client %s" % self.peer)

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
