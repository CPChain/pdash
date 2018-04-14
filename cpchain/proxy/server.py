#!/usr/bin/env python3

# ssl_server.py: SSL server skeleton
# Copyright (c) 2018 Wurong intelligence technology co., Ltd.
# See LICENSE for details.

import sys, os, time


from twisted.internet import reactor, threads, protocol, ssl
from twisted.protocols.basic import NetstringReceiver
from twisted.python import log

from twisted.web.resource import Resource, NoResource, ForbiddenResource
from twisted.web.server import Site
from twisted.web.static import File

from cpchain import config, root_dir
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.message import message_sanity_check, sign_message_verify

from cpchain.storage import IPFSStorage
from cpchain.proxy.proxy_db import Trade, ProxyDB

server_root = os.path.join(config.home, config.proxy.server_root)
server_root = os.path.expanduser(server_root)
os.makedirs(server_root, exist_ok=True)

class SSLServerProtocol(NetstringReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.proxy_db = factory.proxy_db

    def connectionMade(self):
        self.factory.numConnections += 1
        self.peer = str(self.transport.getPeer())
        print("connect to client %s" % self.peer)

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
            trade.seller_addr = data.seller_addr
            trade.buyer_addr = data.buyer_addr
            trade.market_hash = data.market_hash
            trade.AES_key = data.AES_key

            if public_key != data.seller_addr:
                error = "not seller's signature"
                self.proxy_reply_error(error)
                return

            storage = data.storage
            if storage.type == Message.Storage.IPFS:
                ipfs = storage.ipfs
                trade.file_hash = ipfs.file_hash
                if(proxy_db.count(trade)):
                    error = "trade record already in database"
                    self.proxy_reply_error(error)
                    return
                else:
                    file_path = os.path.join(server_root,
                                    trade.file_hash.decode())

                    # seller sold the same file to another buyer
                    if os.path.isfile(file_path):
                        mtime = time.time()
                        os.utime(file_path, (mtime, mtime))
                        proxy_db.insert(trade)
                        self.proxy_reply_success()
                        return
                    else:
                        d = threads.deferToThread(
                                        self.get_ipfs_file,
                                        ipfs.gateway,
                                        trade.file_hash)

                        d.addBoth(self.ipfs_callback)

            elif storage.type == Message.Storage.S3:
                error = "not support S3 storage yet"
                self.proxy_reply_error(error)
                return

        elif message.type == Message.BUYER_DATA:
            data = message.buyer_data
            trade.seller_addr = data.seller_addr
            trade.buyer_addr = data.buyer_addr
            trade.market_hash = data.market_hash

            if public_key != data.buyer_addr:
                error = "not buyer's signature"
                self.proxy_reply_error(error)
                return

            if proxy_db.count(trade):
                self.trade = proxy_db.query(trade)
                self.proxy_reply_success()
                return
            else:
                error = "trade record not found in database"
                self.proxy_reply_error(error)
                return


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
        else:
            error = "failed to get file from ipfs"
            self.proxy_reply_error(error)

    def connectionLost(self, reason):
        self.factory.numConnections -= 1
        print("lost connection to client %s" % self.peer)

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
        else:
            return ForbiddenResource()


def start_ssl_server():

    log.startLogging(sys.stdout)

    # control channel
    factory = SSLServerFactory()
    control_port = config.proxy.server_ctrl_port

    server_key = os.path.expanduser(
                    os.path.join(config.home,
                                config.proxy.server_key))
    server_crt = os.path.expanduser(
                    os.path.join(config.home,
                                config.proxy.server_crt))

    if not os.path.isfile(server_key):
        print("SSL key/cert file not found, run local self-test by default")
        server_key = os.path.join(root_dir, config.proxy.server_key)
        server_crt = os.path.join(root_dir, config.proxy.server_crt)

    reactor.listenSSL(control_port, factory,
            ssl.DefaultOpenSSLContextFactory(
            server_key, server_crt))

    # data channel
    data_port = config.proxy.server_data_port
    file_factory = Site(FileServer())
    reactor.listenSSL(data_port, file_factory,
            ssl.DefaultOpenSSLContextFactory(
            server_key, server_crt))

    reactor.run()



if __name__ == '__main__':
    start_ssl_server()
