#!/usr/bin/env python3

# ssl_client.py: SSL client skeleton
# Copyright (c) 2018 Wurong intelligence technology co., Ltd.
# See LICENSE for details.

import sys

from twisted.internet import reactor, protocol, ssl, defer
from twisted.python import log

class SSLClientProtocol(protocol.Protocol):
    def connectionMade(self):
        self.transport.write(b"hello, world!")

    def dataReceived(self, data):
        print ("server said:", data)
        self.transport.loseConnection()

    def connectionLost(self, reason):
        print ("connection lost: ", reason)


class SSLClientFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):
        return SSLClientProtocol()

    def clientConnectionFailed(self, connector, reason):
        print ("connection failed.")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print ("connection lost.")
        reactor.stop()


def main():
    HOSTNAME = 'cpctest.com'
    PORT = 8000

    factory = SSLClientFactory()
    reactor.connectSSL(HOSTNAME, PORT, factory,
            ssl.ClientContextFactory())
    reactor.run()

    log.startLogging(sys.stdout)

if __name__ == '__main__':
    main()