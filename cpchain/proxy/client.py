#!/usr/bin/env python3

import sys, os

from twisted.internet import reactor, protocol, ssl, defer
from twisted.protocols.basic import NetstringReceiver
from twisted.python import log

from cpchain import config, root_dir
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

            if not proxy_reply.error and self.factory.need_download_file:
                    d = download_file(proxy_reply.file_uuid)
                    self.reply_message = message
                    d.addBoth(self.download_finish)
            else:
                self.factory.d.callback(message)

        else:
            # should never happen
            message = proxy_reply_error("wrong server response")
            self.factory.d.callback(message)

        self.transport.loseConnection()

    def connectionLost(self, reason):
        print("lost connection to client %s" % (self.peer))

    def download_finish(self, result):
        self.factory.d.callback(self.reply_message)


class SSLClientFactory(protocol.ClientFactory):

    def __init__(self, sign_message):
        self.sign_message = sign_message
        self.need_download_file = False

    def buildProtocol(self, addr):
        return SSLClientProtocol(self)

    def clientConnectionFailed(self, connector, reason):
        message = proxy_reply_error("connection failed")
        self.d.callback(message)


def proxy_reply_error(error):
    message = Message()
    message.type = Message.PROXY_REPLY
    proxy_reply = message.proxy_reply
    proxy_reply.error = error
    return message


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

    d = defer.Deferred()
    factory = SSLClientFactory(sign_message)
    factory.d = d

    if message.type == Message.BUYER_DATA:
        factory.need_download_file = True

    reactor.connectSSL(host, ctrl_port, factory,
            ssl.ClientContextFactory())

    return d


def download_file(file_uuid):
    host = config.proxy.server_host
    data_port = config.proxy.server_data_port
    file_dir = os.path.expanduser(config.wallet.download_dir)
    # create if not exists
    os.makedirs(file_dir, exist_ok=True)

    url = "https://%s:%d/%s" % (host, data_port, file_uuid)

    file_path = os.path.join(file_dir, file_uuid)

    _sslverify.platformTrust = lambda : None
    f = open(file_path, 'wb')
    d = treq.get(url)
    d.addCallback(treq.collect, f.write)
    d.addBoth(lambda _: f.close())
    return d


def handle_proxy_response(message):

    assert message.type == Message.PROXY_REPLY

    proxy_reply = message.proxy_reply

    if not proxy_reply.error:
        print('file_uuid: %s' % proxy_reply.file_uuid)
        print('AES_key: %s' % proxy_reply.AES_key.decode())
    else:
        print(proxy_reply.error)

if __name__ == '__main__':

    test_type = 'buyer_data'

    buyer_private_key = None
    buyer_private_key = b'\xa6\xf8_\xee\x1c\x85\xc5\x95\x8d@\x9e\xfa\x80\x7f\xb6\xe0\xb4u\x12\xb6\xdf\x00\xda4\x98\x8e\xaeR\x89~\xf6\xb5'
    buyer_private_key, buyer_public_key = \
                ECCipher.generate_key_pair(buyer_private_key)


    seller_private_key = None
    seller_private_key = b'\xa6\xf8_\xee\x1c\x85\xc5\x95\x8d@\x9e\xfa\x80\x7f\xb6\xe0\xb4u\x12\xb6\xdf\x00\xda4\x98\x8e\xaeR\x89~\xf6\xb5'
    seller_private_key, seller_public_key = \
                ECCipher.generate_key_pair(seller_private_key)

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

        sign_message = SignMessage()
        sign_message.public_key = seller_public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.generate_signature(
                                seller_private_key,
                                sign_message.data
                            )

        d = start_client(sign_message)

        d.addBoth(handle_proxy_response)
        d.addBoth(lambda _: reactor.stop())

    elif test_type == 'buyer_data':
        message = Message()
        buyer_data = message.buyer_data
        message.type = Message.BUYER_DATA
        buyer_data.order_id = 1
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

        d = start_client(sign_message)
        d.addBoth(handle_proxy_response)
        d.addBoth(lambda _: reactor.stop())

    elif test_type == 'proxy_reply':
        message = Message()
        message.type = Message.PROXY_REPLY
        proxy_reply = message.proxy_reply
        proxy_reply.error = "error"
        sign_message = SignMessage()
        sign_message.public_key = seller_public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.generate_signature(
                                seller_private_key,
                                sign_message.data
                            )

        d = start_client(sign_message)
        d.addBoth(handle_proxy_response)
        d.addBoth(lambda _: reactor.stop())

    reactor.run()
