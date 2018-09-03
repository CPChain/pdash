#!/usr/bin/env python3

import os
import logging
import json

from twisted.internet import reactor, protocol, ssl, defer
from twisted.protocols.basic import NetstringReceiver

import treq

from cpchain import config
from cpchain.proxy.msg.trade_msg_pb2 import Message
from cpchain.proxy.message import message_sanity_check

from cpchain.proxy.kadnet import KadNode
from cpchain.proxy.centralnet import Slave

logger = logging.getLogger(__name__)

class SSLClientProtocol(NetstringReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.sign_message = self.factory.sign_message

        self.peer = None
        self.proxy_reply = None

    def connectionMade(self):
        self.peer = self.transport.getPeer()
        logger.debug("connect to server %s" % str(self.peer))

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

        self.proxy_reply = proxy_reply

        self.transport.loseConnection()

    def connectionLost(self, reason):
        logger.debug("lost connection to client %s" % str(self.peer))

        if not self.proxy_reply:
            # Connection may lost after client sent request to proxy
            # but not received any response yet.
            self.proxy_reply = proxy_reply_error("connection Lost")

        self.factory.d.callback(self.proxy_reply)


class SSLClientFactory(protocol.ClientFactory):

    def __init__(self):
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


class ProxyClient:
    def __init__(self, addr):
        self.host = str(addr[0])
        self.port = int(addr[1])

        self.factory = SSLClientFactory()
        self.factory.sign_message = None
        self.trans = None

    def run(self, sign_message):

        message = Message()
        message.ParseFromString(sign_message.data)
        valid = message_sanity_check(message)
        if not valid:
            logger.error("wrong message format")
            return

        self.factory.sign_message = sign_message

        self.trans = reactor.connectSSL(
            self.host,
            self.port,
            self.factory,
            ssl.ClientContextFactory()
            )

        return self.factory.d

    def stop(self):
        self.trans.disconnect()


def download_file(url):

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

    # create if not exists
    os.makedirs(file_dir, exist_ok=True)

    file_name = os.path.basename(url)
    file_path = os.path.join(file_dir, file_name)

    f = open(file_path, 'wb')
    d = treq.get(url, agent=no_verify_agent())
    d.addCallback(treq.collect, f.write)
    d.addBoth(lambda _: f.close())
    return d

def pick_proxy():
    return Slave().pick_peer()

def start_proxy_request(sign_message, proxy_id):
    '''send request to proxy server

    Args:
        sign_message: request message
        proxy_id: proxy eth addr

    Returns:
        tuple: (error, AES_key, urls)
    '''

    d = defer.Deferred()

    def run_client_done(proxy_reply, ip):
        if not proxy_reply.error:
            urls = concat_url(ip, proxy_reply)
            d.callback((None, proxy_reply.AES_key, urls))
        else:
            d.callback((proxy_reply.error, None, None))

    def get_proxy_done(proxy_addr):
        if proxy_addr:
            proxy_client = ProxyClient(proxy_addr)
            proxy_client.run(sign_message).addCallback(run_client_done, proxy_addr[0])

        else:
            d.callback(('failed to get proxy addr', None, None))

    get_proxy(proxy_id).addCallback(get_proxy_done)

    return d

def get_proxy(proxy_id):
    return KadNode().get_peer(proxy_id)

def concat_url(ip, proxy_reply):

    if proxy_reply.error:
        return

    port_conf = json.loads(proxy_reply.port_conf)

    urls = []

    if 'file' in port_conf:
        port = int(port_conf['file'])
        url = 'https://%s:%d/%s' % (ip, port, proxy_reply.data_path)
        urls.append(url)

    if 'stream_ws' in port_conf:
        port = int(port_conf['stream_ws'])
        url = 'ws://%s:%d/%s' % \
            (ip, port, proxy_reply.data_path)
        urls.append(url)

    if 'stream_restful' in port_conf:
        port = int(port_conf['stream_restful'])
        url = 'http://%s:%d/%s' % \
            (ip, port, proxy_reply.data_path)
        urls.append(url)

    return urls
