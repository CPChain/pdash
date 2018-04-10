#!/usr/bin/env python3

# ssl_client.py: SSL client skeleton
# Copyright (c) 2018 Wurong intelligence technology co., Ltd.
# See LICENSE for details.

import sys, os

from twisted.internet import reactor, protocol, ssl, defer
from twisted.protocols.basic import NetstringReceiver
from twisted.python import log

from cpchain import config
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.message import message_sanity_check
from cpchain.crypto import ECCipher

from twisted.internet import _sslverify
import treq

class SSLClientProtocol(NetstringReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.sign_message = self.factory.sign_message

    def connectionMade(self):
        self.peer = str(self.transport.getPeer())
        print("connect to server %s" % self.peer)

        string = self.sign_message.SerializeToString()
        self.sendString(string)

    def stringReceived(self, string):
        message = Message()
        message.ParseFromString(string)
        valid = message_sanity_check(message)
        if valid and message.type == Message.PROXY_REPLY:
            proxy_reply = message.proxy_reply
            self.sign_message.data = message.SerializeToString()

            if proxy_reply.error:
                print('error: %s' % proxy_reply.error)
            else:
                print('AES_key: %s' % proxy_reply.AES_key.decode())
                print('file_uuid: %s' % proxy_reply.file_uuid)
                if self.factory.need_download_file:
                    d = download_file(proxy_reply.file_uuid)
                    d.addBoth(lambda _: reactor.stop())
        else:
            print("wrong server response")

        self.transport.loseConnection()

    def connectionLost(self, reason):
        print("lost connection to client %s" % (self.peer))


class SSLClientFactory(protocol.ClientFactory):

    def __init__(self, sign_message):
        self.sign_message = sign_message
        self.need_download_file = False

    def buildProtocol(self, addr):
        return SSLClientProtocol(self)

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        if not self.need_download_file:
            reactor.stop()


def start_client(sign_message):

    log.startLogging(sys.stdout)

    host = config.proxy.server_host
    ctrl_port = config.proxy.server_ctrl_port

    message = Message()
    message.ParseFromString(sign_message.data)
    valid = message_sanity_check(message)
    if not valid:
        print("wrong message format")
        return

    factory = SSLClientFactory(sign_message)

    if message.type == Message.BUYER_DATA:
        factory.need_download_file = True

    reactor.connectSSL(host, ctrl_port, factory,
            ssl.ClientContextFactory())

    reactor.run()


def download_file(file_uuid, file_dir=None):
    host = config.proxy.server_host
    data_port = config.proxy.server_data_port

    url = "https://%s:%d/%s" % (host, data_port, file_uuid)

    file_dir = file_dir or os.getcwd()
    file_path = os.path.join(file_dir, file_uuid)

    _sslverify.platformTrust = lambda : None
    f = open(file_path, 'wb')
    d = treq.get(url)
    d.addCallback(treq.collect, f.write)
    d.addBoth(lambda _: f.close())
    return d


if __name__ == '__main__':

    test_type = 'buyer_data'

    buyer_private_key = None
    buyer_private_key = b'0\x81\xec0W\x06\t*\x86H\x86\xf7\r\x01\x05\r0J0)\x06\t*\x86H\x86\xf7\r\x01\x05\x0c0\x1c\x04\x08\x85c\xfe}\x89?\xd2k\x02\x02\x08\x000\x0c\x06\x08*\x86H\x86\xf7\r\x02\t\x05\x000\x1d\x06\t`\x86H\x01e\x03\x04\x01*\x04\x10\x10\xdf\x02\x0e\xe6\xdcy\xce\x16\xbb\x8e\x03\xc9\xa6\xe9\xf1\x04\x81\x90\xd1\xfd\x0e\x01\'\xeb\x04\xb6\tHi\x14\x0bN\xabp"$\x04\xcc;\xadh\x07-\xc9\xd3\xe8\xc4\xcb\x8d\xfc\x10\xd0$\xab <#5\n\x1b\xe9\xafL\x8b\x06\xb2\x99\xab\x8a-\xed\x90\xf4\xd7\x99\x10\xf6\xc9\\m#\xdeqW\xc3 \xff\xd4d`\n\xedm\x98Mig\xdc\xac\x87A\x9f\xe4\xef,\xcf\xc9\xec\xc2|\x85M\xc9v7(\x00\x08\xdb\xeeq\xa0\xf8:\xde\xa9sV\xa9\x0fs\x80d&3\\f\x94\xd0\x19\xfd\x9cJ\xa5W\x86\x0f\xd88\xff\x1d]\xd6\xb5E\xa1Z\xf7\x15\x81,\x8d'
    buyer_private_key, buyer_public_key = \
                ECCipher.generate_key_pair(buyer_private_key)

    seller_private_key = None
    seller_private_key = b'0\x81\xec0W\x06\t*\x86H\x86\xf7\r\x01\x05\r0J0)\x06\t*\x86H\x86\xf7\r\x01\x05\x0c0\x1c\x04\x08\xc7\x05\xb9\xa9\xbew\xdf$\x02\x02\x08\x000\x0c\x06\x08*\x86H\x86\xf7\r\x02\t\x05\x000\x1d\x06\t`\x86H\x01e\x03\x04\x01*\x04\x10P\xf8\t\xf3\x1eL\xd5\x1c4H\x9e2\x8b\xcbv0\x04\x81\x90V\xfe^\xcf"j\x86\x1a\xf1_\xab\x96\xd6{;{K3o~\xe9\xc4\xc5\xbb\xd2\xe2\xbeI3\x08\xc1\xeb\xdbuQJ\xd3\xfat\xb4W;60d\nAy\xe0\x08\x10\xeb\x9bM\xb4\xad\xe0e\xd1\xd5\xafX\xd5\x83\xb6\xc6\'\x82\xd2\x8e\xd0\x08y\xc1w\x19\xf8P>\xf9\xe4\x95\xe3\x17\x82\xce\xb9\xdb?\xdc\x10\xa5Z\xd3\xaef\x0e\x90\x8d\x7fkA\r\xaaD\x1d\xde\xc7J\x86e\xee\x9d\x1b\xb0\x16W\xb7\xab\xc35X\xae\x16\xad\xb5\r\x82\x91Djt"\xed#\xcc\xde\xe1\xa4\xe9Ww\xf6\x87'
    seller_private_key, seller_public_key = \
                ECCipher.generate_key_pair(seller_private_key)

    if test_type == 'seller_data':
        message = Message()
        seller_data = message.seller_data
        message.type = Message.SELLER_DATA
        seller_data.seller_addr = seller_public_key
        seller_data.buyer_addr = buyer_public_key
        seller_data.market_hash = b'MARKET_HASH'
        seller_data.AES_key = b'AES_key'
        storage = seller_data.storage
        storage.type = Message.Storage.IPFS
        ipfs = storage.ipfs
        ipfs.file_hash = b'QmT4kFS5gxzQZJwiDJQ66JLVGPpyTCF912bywYkpgyaPsD'
        ipfs.gateway = "192.168.0.132:5001"

        sign_message = SignMessage()
        sign_message.public_key = seller_public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.generate_signature(
                                seller_private_key,
                                sign_message.data
                            )

        start_client(sign_message)

        message = Message()
        message.ParseFromString(sign_message.data)
        proxy_reply = message.proxy_reply
        if not proxy_reply.error:
            print('succeed to upload trade data')
            print('file_uuid: %s' % proxy_reply.file_uuid)
        else:
            print(proxy_reply.error)

    elif test_type == 'buyer_data':
        message = Message()
        buyer_data = message.buyer_data
        message.type = Message.BUYER_DATA
        buyer_data.seller_addr = seller_public_key
        buyer_data.buyer_addr = buyer_public_key
        buyer_data.market_hash = b'MARKET_HASH'

        sign_message = SignMessage()
        sign_message.public_key = buyer_public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.generate_signature(
                                buyer_private_key,
                                sign_message.data
                            )

        start_client(sign_message)
        message = Message()
        message.ParseFromString(sign_message.data)

        proxy_reply = message.proxy_reply
        if proxy_reply.error:
            print(proxy_reply.error)
        else:
            print('AES_key: %s' % proxy_reply.AES_key.decode())
            print('file_uuid: %s' % proxy_reply.file_uuid)

    elif test_type == 'proxy_reply':
        message = Message()
        message.type = Message.PROXY_REPLY
        proxy_reply = message.proxy_reply
        proxy_reply.error = "error"
        sign_message = SignMessage()
        sign_message.public_key = seller_public_key
        sign_message.data = message.SerializeToString()
        seller_ec.generate_signature(sign_message.data)
        sign_message.signature = seller_ec.decode_signature()

        start_client(sign_message)
        message = Message()
        message.ParseFromString(sign_message.data)

        proxy_reply = message.proxy_reply
        if proxy_reply.error:
            print(proxy_reply.error)


