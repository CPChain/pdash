#!/usr/bin/env python3

# ssl_client.py: SSL client skeleton
# Copyright (c) 2018 Wurong intelligence technology co., Ltd.
# See LICENSE for details.

import sys, os

from twisted.internet import reactor, protocol, ssl, defer
from twisted.protocols.basic import NetstringReceiver
from twisted.python import log

from cpchain import config
from cpchain.proxy.msg.trade_msg_pb2 import Message
from cpchain.proxy.message import message_sanity_check, proxy_reply_copy

import requests

class SSLClientProtocol(NetstringReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.message = self.factory.message

    def connectionMade(self):
        self.peer = str(self.transport.getPeer())
        print("connect to server " + self.peer)

        string = self.message.SerializeToString()
        self.sendString(string)

    def stringReceived(self, string):
        message = Message()
        message.ParseFromString(string)
        valid = message_sanity_check(message)
        if valid and message.type == Message.PROXY_REPLY:
            proxy_reply = message.proxy_reply
            proxy_reply_copy(proxy_reply,
                            self.message.proxy_reply)

            if proxy_reply.error:
                print('error: ' + proxy_reply.error)
            else:
                print('AES_key: ' + proxy_reply.AES_key.decode())
                print('file_hash: ' + proxy_reply.file_hash.decode())
                print('file_size: ' + str(proxy_reply.file_size))
        else:
            print("wrong server response")

        self.transport.loseConnection()

    def connectionLost(self, reason):
        print("lost connection to client %s" % (self.peer))

class SSLClientFactory(protocol.ClientFactory):
    def __init__(self, message):
        self.message = message

    def buildProtocol(self, addr):
        return SSLClientProtocol(self)

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        reactor.stop()


def start_client(message):

    host = config.proxy.server_host
    ctrl_port = config.proxy.server_ctrl_port

    valid = message_sanity_check(message)
    if not valid:
        print("wrong message format")
        return

    factory = SSLClientFactory(message)
    reactor.connectSSL(host, ctrl_port, factory,
            ssl.ClientContextFactory())
    reactor.run()

    log.startLogging(sys.stdout)


def download_file(file_hash, dir=os.getcwd()):
    host = config.proxy.server_host
    data_port = config.proxy.server_data_port

    url = 'https://' + host + ':' + str(data_port)\
             + '/' + file_hash.decode()

    r = requests.get(url, stream=True, verify=False)

    with open(dir + '/' + file_hash.decode(), 'wb') as fd:
        for chunk in r.iter_content(8192):
            fd.write(chunk)

        fd.close()


if __name__ == '__main__':

    test_type = "buyer_data"

    message = Message()
    if test_type == "seller_data":
        data = message.seller_data
        message.type = Message.SELLER_DATA
        data.seller_addr = b'SELLER_ADDR'
        data.buyer_addr = b'BUYER_ADDR'
        data.market_hash = b'MARKET_HASH'
        data.AES_key = b'AES_key'
        storage = data.storage
        storage.type = Message.Storage.IPFS
        ipfs = storage.ipfs
        ipfs.file_hash = b'QmVSdf3qf7kGhaQF2CKFTKN3gwuhz1wcoQBJNCmB4yGzPM'
        ipfs.gateway = "192.168.0.132:5001"
        start_client(message)
        proxy_reply = message.proxy_reply
        if not proxy_reply.error:
            print('succeed to upload trade data')
        else:
            print(proxy_reply.error)
    elif test_type == "buyer_data":
        data = message.buyer_data
        message.type = Message.BUYER_DATA
        data.seller_addr = b'SELLER_ADDR'
        data.buyer_addr = b'BUYER_ADDR'
        data.market_hash = b'MARKET_HASH'
        start_client(message)
        proxy_reply = message.proxy_reply
        if proxy_reply.error:
            print(proxy_reply.error)
        else:
            print('AES_key:')
            print(proxy_reply.AES_key)
            file_hash = proxy_reply.file_hash
            download_file(file_hash)
    elif test_type == "proxy_reply":
        message.type = Message.PROXY_REPLY
        proxy_reply = message.proxy_reply
        proxy_reply.error = "error"
        start_client(message)


