#!/usr/bin/env python3

import os
import logging

from twisted.internet import reactor, protocol, ssl, defer
from twisted.protocols.basic import NetstringReceiver

import treq

from cpchain import config
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.message import message_sanity_check

logger = logging.getLogger(__name__)

class SSLClientProtocol(NetstringReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.sign_message = self.factory.sign_message

        self.peer = None

    def connectionMade(self):
        self.peer = str(self.transport.getPeer())
        logger.debug("connect to server %s" % self.peer)

        string = self.sign_message.SerializeToString()
        self.sendString(string)

    def stringReceived(self, string):
        message = Message()
        message.ParseFromString(string)
        valid = message_sanity_check(message)

        if not valid or message.type != Message.PROXY_REPLY:
            # should never happen
            proxy_reply = proxy_reply_error("wrong server response")
        else:
            proxy_reply = message.proxy_reply

        self.factory.d.callback(proxy_reply)

        self.transport.loseConnection()

    def connectionLost(self, reason):
        logger.debug("lost connection to client %s" % (self.peer))


class SSLClientFactory(protocol.ClientFactory):

    def __init__(self, sign_message):
        self.sign_message = sign_message
        self.d = defer.Deferred()

    def buildProtocol(self, addr):
        return SSLClientProtocol(self)

    def clientConnectionFailed(self, connector, reason):
        proxy_reply = proxy_reply_error("connection failed")
        self.d.callback(proxy_reply)


def proxy_reply_error(error):
    message = Message()
    message.type = Message.PROXY_REPLY
    proxy_reply = message.proxy_reply
    proxy_reply.error = error
    return proxy_reply


def start_client(sign_message, addr=None):

    if addr:
        host = str(addr[0])
        port = int(addr[1])
    else:
        host = config.proxy.server_host
        port = config.proxy.server_ctrl_port

    message = Message()
    message.ParseFromString(sign_message.data)
    valid = message_sanity_check(message)
    if not valid:
        logger.error("wrong message format")
        return

    factory = SSLClientFactory(sign_message)

    reactor.connectSSL(host, port, factory,
                       ssl.ClientContextFactory())

    buyer_request = message.type == Message.BUYER_DATA

    d = defer.Deferred()

    def handle_proxy_response(proxy_reply):

        if not proxy_reply.error:
            logger.debug('file_uri: %s' % proxy_reply.file_uri)
            logger.debug('AES_key: %s' % proxy_reply.AES_key.decode())
            if buyer_request:
                return download_file(proxy_reply.file_uri).addCallback(
                    lambda _: d.callback(proxy_reply))
        else:
            logger.debug(proxy_reply.error)

        d.callback(proxy_reply)

    factory.d.addCallback(handle_proxy_response)

    return d



def download_file(uri):

    from twisted.web.iweb import IPolicyForHTTPS
    from zope.interface import implementer
    from treq import api

    @implementer(IPolicyForHTTPS)
    class NoVerifySSLContextFactory(object):
        """Context that doesn't verify SSL connections"""
        def creatorForNetloc(self, hostname, port): # pylint: disable=unused-argument
            return ssl.CertificateOptions(verify=False)

    def no_verify_agent(**kwargs):
        reactor = api.default_reactor(kwargs.get('reactor'))
        pool = api.default_pool(
            reactor,
            kwargs.get('pool'),
            kwargs.get('persistent'))

        no_verify_agent.agent = api.Agent(
            reactor,
            contextFactory=NoVerifySSLContextFactory(),
            pool=pool
        )
        return no_verify_agent.agent

    file_dir = os.path.expanduser(config.wallet.download_dir)
    # create if not exists
    os.makedirs(file_dir, exist_ok=True)

    file_name = os.path.basename(uri)
    file_path = os.path.join(file_dir, file_name)

    f = open(file_path, 'wb')
    d = treq.get(uri, agent=no_verify_agent())
    d.addCallback(treq.collect, f.write)
    d.addBoth(lambda _: f.close())
    return d


# Code below for testing purpose only, pls. ignore.
# Will be removed in formal release.
if __name__ == '__main__':

    from cpchain.account import Accounts
    from cpchain.crypto import ECCipher # pylint: disable=no-name-in-module

    import sys
    from twisted.python import log as twisted_log
    twisted_log.startLogging(sys.stdout)

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


    test_type = 'buyer_data'

    if test_type == 'seller_data':
        message = Message()
        seller_data = message.seller_data
        message.type = Message.SELLER_DATA
        seller_data.order_id = 1
        seller_data.seller_addr = seller_addr
        seller_data.buyer_addr = buyer_addr
        seller_data.market_hash = 'MARKET_HASH'
        seller_data.AES_key = b'AES_key'
        storage = seller_data.storage
        storage.type = Message.Storage.IPFS
        ipfs = storage.ipfs
        ipfs.file_hash = b'QmT4kFS5gxzQZJwiDJQ66JLVGPpyTCF912bywYkpgyaPsD'
        ipfs.gateway = "192.168.0.132:5001"

        sign_message = SignMessage()
        sign_message.public_key = seller_public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.create_signature(
            seller_private_key,
            sign_message.data
            )

        d = start_client(sign_message)
        d.addBoth(lambda _: reactor.stop())

    elif test_type == 'buyer_data':
        message = Message()
        buyer_data = message.buyer_data
        message.type = Message.BUYER_DATA
        buyer_data.order_id = 1
        buyer_data.seller_addr = seller_addr
        buyer_data.buyer_addr = buyer_addr
        buyer_data.market_hash = 'MARKET_HASH'

        sign_message = SignMessage()
        sign_message.public_key = buyer_public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.create_signature(
            buyer_private_key,
            sign_message.data
            )

        d = start_client(sign_message)
        d.addBoth(lambda _: reactor.stop())

    elif test_type == 'proxy_reply':
        message = Message()
        message.type = Message.PROXY_REPLY
        proxy_reply = message.proxy_reply
        proxy_reply.error = "error"
        sign_message = SignMessage()
        sign_message.public_key = seller_public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.create_signature(
            seller_private_key,
            sign_message.data
            )

        d = start_client(sign_message)
        d.addBoth(lambda _: reactor.stop())

    reactor.run()
