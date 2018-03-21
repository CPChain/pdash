#!/usr/bin/env python3

# ssl_server.py: SSL server skeleton
# Copyright (c) 2018 Wurong intelligence technology co., Ltd.
# See LICENSE for details.

import sys

from twisted.internet import reactor, protocol, ssl, defer
from twisted.python import log

class SSLServerProtocol(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.numConnections += 1

    def dataReceived(self, data):
        print (data, " received from ",
                self.transport.getPeer())
        self.transport.write(data)

    def connectionLost(self, reason):
        self.factory.numConnections -= 1


class SSLServerFactory(protocol.Factory):
    numConnections = 0

    def buildProtocol(self, addr):
        return SSLServerProtocol(self)


def main():
    PORT = 8000
    factory = SSLServerFactory()

    reactor.listenSSL(8000, factory,
            ssl.DefaultOpenSSLContextFactory(
            'key/server_no_pass.key', 'key/server.crt'))
    reactor.run()

    log.startLogging(sys.stdout)

if __name__ == '__main__':
    main()