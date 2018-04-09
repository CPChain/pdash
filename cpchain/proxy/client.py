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
from cpchain.proxy.crypto import ECCipher

import requests

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
        else:
            print("wrong server response")

        self.transport.loseConnection()

    def connectionLost(self, reason):
        print("lost connection to client %s" % (self.peer))

class SSLClientFactory(protocol.ClientFactory):

    def __init__(self, sign_message):
        self.sign_message = sign_message

    def buildProtocol(self, addr):
        return SSLClientProtocol(self)

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
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
    reactor.connectSSL(host, ctrl_port, factory,
            ssl.ClientContextFactory())

    reactor.run()


def download_file(file_uuid, file_dir=None):
    host = config.proxy.server_host
    data_port = config.proxy.server_data_port

    url = "https://%s:%d/%s" % (host, data_port, file_uuid)

    r = requests.get(url, stream=True, verify=False)

    file_dir = file_dir or os.getcwd()

    file_path = os.path.join(file_dir, file_uuid)

    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)


if __name__ == '__main__':

    test_type = 'buyer_data'

    buyer_ec = ECCipher()
    buyer_ec.generate_key_pair()
    # buyer_ec.load_private_key(b'-----BEGIN ENCRYPTED PRIVATE KEY-----\nMIIBHDBXBgkqhkiG9w0BBQ0wSjApBgkqhkiG9w0BBQwwHAQIbzYaJ4JPS6wCAggA\nMAwGCCqGSIb3DQIJBQAwHQYJYIZIAWUDBAEqBBAX+qu82h57tKzx1Umoir82BIHA\napI6llFcSIH9xm+y7rGVX8IoTKVXhS+8QE7JzGgqOidMgx00NQRk+da3BrgD206o\n1pkuzEBDF+7xMl8YheADlgG5ER19kQzGdMge+2WrKY5j0/R7bgtXNMNtc/WCPV+h\ngvUm/UG1YTErqTaMRyiQdqUJm9OnY6+lcgSN4haHwJlJbEBQprGAC1GXfB3d8c57\nWC+j81tm03sG6k1eMVM0juDLfqGeztjT9jb6hzo3Whd3uXhyUtiNLSfmw8OcOQPa\n-----END ENCRYPTED PRIVATE KEY-----\n')
    buyer_private_key = buyer_ec.get_private_key()
    buyer_public_key = buyer_ec.get_public_key()


    seller_ec = ECCipher()
    seller_ec.generate_key_pair()
    # seller_ec.load_private_key(b'-----BEGIN ENCRYPTED PRIVATE KEY-----\nMIIBHDBXBgkqhkiG9w0BBQ0wSjApBgkqhkiG9w0BBQwwHAQIj8Rr8Z6IA0gCAggA\nMAwGCCqGSIb3DQIJBQAwHQYJYIZIAWUDBAEqBBDK/EY6d5mOIhuPbVDstdIgBIHA\nuhvOq3d24avHR3AvuF6BDVQd/Y+esghw/ImH5EYDZQkQJwABt/92IpPQgDA+0s76\n4+WYR3oTd/NfexqInfBvLrow1PQwDLTY+Em5nogW+eWYN+IsWjI4xv/S0/O07cpD\ndQw9gbTgyVf0FPBBpEQDDW8Ido0p8cjzV0/DUmty4ObExyzmkmbd597KfDVn02sx\nL4huvVM2/u+Tzww8VpwuuyQQtzMh393ZE6LRATLAQv1ihVj98GdzWNTUWtNA7Vk9\n-----END ENCRYPTED PRIVATE KEY-----\n')
    seller_public_key = seller_ec.get_public_key()
    seller_private_key = seller_ec.get_private_key()

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
        sign_message.public_key = seller_data.seller_addr
        sign_message.data = message.SerializeToString()
        seller_ec.generate_signature(sign_message.data)
        sign_message.signature = seller_ec.decode_signature()

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
        sign_message.public_key = buyer_data.buyer_addr
        sign_message.data = message.SerializeToString()
        buyer_ec.generate_signature(sign_message.data)
        sign_message.signature = buyer_ec.decode_signature()

        start_client(sign_message)
        message = Message()
        message.ParseFromString(sign_message.data)

        proxy_reply = message.proxy_reply
        if proxy_reply.error:
            print(proxy_reply.error)
        else:
            print('AES_key: %s' % proxy_reply.AES_key.decode())
            print('file_uuid: %s' % proxy_reply.file_uuid)
            file_uuid = proxy_reply.file_uuid
            download_file(file_uuid)

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


