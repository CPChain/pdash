#!/usr/bin/env python3

# ssl_server.py: SSL server skeleton
# Copyright (c) 2018 Wurong intelligence technology co., Ltd.
# See LICENSE for details.

import sys, os

from twisted.internet import reactor, protocol, ssl, defer
from twisted.protocols.basic import NetstringReceiver
from twisted.python import log

from cpchain import config, root_dir
from cpchain.proxy.msg.trade_msg_pb2 import Message
from cpchain.proxy.message import message_sanity_check
from cpchain.proxy.ipfs import IPFS
from cpchain.proxy.proxy_db import Trade, ProxyDB

server_root = os.path.join(root_dir, config.proxy.server_root)

class SSLServerProtocol(NetstringReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.proxy_db = factory.proxy_db

    def connectionMade(self):
        self.factory.numConnections += 1
        self.peer = str(self.transport.getPeer())
        print("connect to client " + self.peer)

    def stringReceived(self, string):
        proxy_db = self.proxy_db
        trade = Trade()
        error = None
        file_size = 0

        message = Message()
        message.ParseFromString(string)
        valid = message_sanity_check(message)
        if not valid or message.type == Message.PROXY_REPLY:
            error = "wrong client request"

        elif message.type == Message.SELLER_DATA:
            data = message.seller_data
            trade.seller_addr = data.seller_addr
            trade.buyer_addr = data.buyer_addr
            trade.market_hash = data.market_hash
            trade.AES_key = data.AES_key

            storage = data.storage
            if storage.type == Message.Storage.IPFS:
                ipfs = storage.ipfs
                trade.file_hash = ipfs.file_hash
                if(proxy_db.count(trade)):
                    error = "trade record already in database"
                else:
                    host, port = ipfs.gateway.strip().split(':')
                    ipfs = IPFS()
                    if ipfs.connect(host, port) and \
                        ipfs.get_file(trade.file_hash):
                        file_path = server_root + '/' + trade.file_hash.decode()
                        file_size = os.path.getsize(file_path)
                        proxy_db.insert(trade)
                    else:
                        error = "failed to get file from ipfs"

            elif storage.type == Message.Storage.S3:
                error = "not support S3 storage yet"

        elif message.type == Message.BUYER_DATA:
            data = message.buyer_data
            trade.seller_addr = data.seller_addr
            trade.buyer_addr = data.buyer_addr
            trade.market_hash = data.market_hash
            if proxy_db.count(trade):
                trade = proxy_db.query(trade)[0]
                file_path = server_root + '/' + trade.file_hash.decode()
                file_size = os.path.getsize(file_path)
            else:
                error = "trade record not found in database"

        reply_message = Message()
        reply_message.type = Message.PROXY_REPLY
        proxy_reply = reply_message.proxy_reply

        if error:
            proxy_reply.error = error
        else:
            proxy_reply.AES_key = trade.AES_key
            proxy_reply.file_hash = trade.file_hash
            proxy_reply.file_size = file_size

        string = reply_message.SerializeToString()
        self.sendString(string)
        self.transport.loseConnection()

    def connectionLost(self, reason):
        self.factory.numConnections -= 1
        print("lost connection to client %s" % (self.peer))

class SSLServerFactory(protocol.Factory):
    numConnections = 0


    def buildProtocol(self, addr):
        return SSLServerProtocol(self)

    def startFactory(self):
        self.proxy_db = ProxyDB()
        self.proxy_db.session_create()

    def stopFactory(self):
        self.proxy_db.session_close()
        reactor.stop()


def start_ssl_server():
    factory = SSLServerFactory()

    port = config.proxy.server_port
    server_key = os.path.join(root_dir, config.proxy.server_key)
    server_crt = os.path.join(root_dir, config.proxy.server_crt)

    reactor.listenSSL(port, factory,
            ssl.DefaultOpenSSLContextFactory(
            server_key, server_crt))
    reactor.run()

    log.startLogging(sys.stdout)

if __name__ == '__main__':
    start_ssl_server()
