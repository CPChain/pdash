#!/usr/bin/env python3

# ssl_server.py: SSL server skeleton
# Copyright (c) 2018 Wurong intelligence technology co., Ltd.
# See LICENSE for details.

import sys, os

from file_ops import *

from twisted.internet import reactor, protocol, ssl, defer
from twisted.python import log

TOP_FILE_DIR = '/tmp/cpc_test/server'

class SSLServerProtocol(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.numConnections += 1
        self.request = {
            'tran_state' : 'connect_to_client',
            'fd' : None
            }

        self.peer = str(self.transport.getPeer())
        print("connect to client " + self.peer)

    def dataReceived(self, data):
        if self.request['tran_state'] == 'connect_to_client':
            data = clean_and_split_input(data)
            client_tran_state = data[0]
            if client_tran_state == 'client_put_file_hash':
                self.request['file_hash'] = data[1]
                file_name = data[2]
                self.request['tran_state'] = 'server_get_file_hash'
                self.str_write(self.request['tran_state'] + \
                    ":" + self.request['file_hash'])
                self.request['fd'] = open(TOP_FILE_DIR + "/" + \
                                        file_name, 'wb')
                self.request['tran_state'] = 'server_get_file'

            elif client_tran_state == 'client_list_file':
                for file_name in list_all_files(TOP_FILE_DIR):
                    file_name = file_name[len(TOP_FILE_DIR)+1:]
                    self.str_write(file_name)
                self.request['tran_state'] = 'server_list_file'
                self.transport.loseConnection()
            elif client_tran_state == 'client_get_file_hash':
                self.request['file_path'] = TOP_FILE_DIR + "/" + data[1]
                if not os.path.isfile(self.request['file_path']):
                    self.str_write("remote_file_does_not_exist")
                else:
                    self.request['tran_state'] = 'server_put_file_hash'
                    self.request['file_hash'] = \
                        get_file_md5_hash(self.request['file_path'])
                    self.str_write(self.request['tran_state'] + \
                        ":" + self.request['file_hash'])
            else:
                print(self.peer + " sent wrong data: " + str(data))
                self.transport.loseConnection()

        elif self.request['tran_state'] == 'server_put_file_hash':
            data = clean_and_split_input(data)
            client_tran_state = data[0]
            if client_tran_state == 'client_get_file':
                self.request['tran_state'] = 'server_put_file'
                for byte in read_bytes_from_file(self.request['file_path']):
                    self.transport.write(byte)
            else:
                print("failed at server_put_file_hash")
            self.transport.loseConnection()
        elif self.request['tran_state'] == 'server_get_file':
            self.request['fd'].write(data)

    def connectionLost(self, reason):
        self.factory.numConnections -= 1
        if self.request['fd']:
            self.request['fd'].close()
            if not validate_file_md5_hash(self.request['fd'].name, \
                self.request['file_hash']):
                os.unlink(self.request['fd'].name)
                print("The file is not properly tranmitted.")

        print("lost connection to client %s at %s stage" % (self.peer, \
                self.request['tran_state']))

    def str_write(self, data):
        self.transport.write(data.encode('utf-8'))


class SSLServerFactory(protocol.Factory):
    numConnections = 0

    def buildProtocol(self, addr):
        return SSLServerProtocol(self)


def start_ssl_server(port):
    factory = SSLServerFactory()

    reactor.listenSSL(port, factory,
            ssl.DefaultOpenSSLContextFactory(
            'key/server_no_pass.key', 'key/server.crt'))
    reactor.run()

    log.startLogging(sys.stdout)

if __name__ == '__main__':
    start_ssl_server(8000)
