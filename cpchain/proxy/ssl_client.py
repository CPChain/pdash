#!/usr/bin/env python3

# ssl_client.py: SSL client skeleton
# Copyright (c) 2018 Wurong intelligence technology co., Ltd.
# See LICENSE for details.

import sys, os

from file_ops import *

from twisted.internet import reactor, protocol, ssl, defer
from twisted.python import log

class SSLClientProtocol(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.request = self.factory.request

    def connectionMade(self):
        self.request['tran_state'] = 'connect_to_server'
        self.request['fd'] = None
        self.request['file_list'] = []

        if self.request['cmd'] == 'put':
            self.request['file_hash'] = \
                get_file_md5_hash(self.request['local_file_path'])
            file_name = os.path.basename(\
                            self.request['local_file_path'])
            self.request['tran_state'] = 'client_put_file_hash'
            self.str_write(self.request['tran_state'] + \
                ":" + self.request['file_hash'] + ":" + file_name)
        elif self.request['cmd'] == 'list':
            self.request['tran_state'] = 'client_list_file'
            self.str_write(self.request['tran_state'])
        elif self.request['cmd'] == 'get':
            self.request['tran_state'] = 'client_get_file_hash'
            self.str_write(self.request['tran_state'] + \
                ":" + self.request['remote_file_path'])

        self.peer = str(self.transport.getPeer())
        print("connect to server " + self.peer)

    def dataReceived(self, data):
        if self.request['tran_state'] == 'client_put_file_hash':
            data = clean_and_split_input(data)
            if data[0] == 'server_get_file_hash' \
                and self.request['file_hash'] == data[1]:
                self.request['tran_state'] = 'client_put_file'
                for byte in read_bytes_from_file(\
                                self.request['local_file_path']):
                    self.transport.write(byte)
                self.transport.loseConnection()

            else:
                print("failed at client_put_file_hash")
                self.transport.loseConnection()

        elif self.request['tran_state'] == 'client_list_file':
            self.request['file_list'].append(data.decode())

        elif self.request['tran_state'] == 'client_get_file_hash':
            data = clean_and_split_input(data)
            if data[0] == 'remote_file_does_not_exist':
                print("remote file does not exist")
                self.transport.loseConnection()
            elif data[0] == 'server_put_file_hash':
                self.request['file_hash'] = data[1]
                self.request['tran_state'] = 'client_get_file'
                self.str_write(self.request['tran_state'])
                self.request['fd'] = open(\
                                self.request['local_file_path'], 'wb')

        elif self.request['tran_state'] == 'client_get_file':
            self.request['fd'].write(data)

        else:
            print(self.peer + " sent wrong data: " + data.decode())
            self.transport.loseConnection()

    def connectionLost(self, reason):
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


class SSLClientFactory(protocol.ClientFactory):
    def __init__(self, request):
        self.request = request

    def buildProtocol(self, addr):
        return SSLClientProtocol(self)

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        reactor.stop()



def file_transaction(request):
    """
    file transaction request format:
    {
        'host' : 'cpctest.com',
        'port' : 8000,
        'cmd' : 'put/get/list',
        'remote_file_path' :'remote file path on server',
        'local_file_path' : 'local file path on client'
    }
    """

    host = None
    port = None
    cmd = None
    local_file_path = None
    remote_file_path = None
    error = []

    if type(request) != dict:
        error.append("wrong request format")
        print(error)
        print(file_transaction.__doc__)
        return

    if 'host' in request:
        host = request['host']
    if 'port' in request:
        port = request['port']
    if 'cmd' in request:
        cmd = request['cmd']
    if 'local_file_path' in request:
        local_file_path = request['local_file_path']
    if 'remote_file_path' in request:
        remote_file_path = request['remote_file_path']

    if not host:
        error.append("missing host")
    elif not port:
        error.append("missing port")
    elif not cmd:
        error.append("missing command")
    elif cmd == 'put':
        if not local_file_path:
            error.append("missing local file path")
        else:
            if not os.path.isfile(local_file_path):
                error.append(local_file_path + " file does not exist")

    elif cmd == 'get':
        if not remote_file_path:
            error.append("missing remote file path")

        if not local_file_path:
            error.append("missing local file path")
        else:
            if os.path.isfile(local_file_path):
                error.append(local_file_path + " file already exists")

            local_file_dir = os.path.dirname(local_file_path)
            if not os.path.isdir(local_file_dir):
                error.append("local file dir doesn't exist")

    elif cmd != 'list':
        error.append("wrong command")

    if len(error):
        print(error)
        print(file_transaction.__doc__)
        return error

    start_client(request)


def start_client(request):

    host = request['host']
    port = request['port']

    factory = SSLClientFactory(request)
    reactor.connectSSL(host, port, factory,
            ssl.ClientContextFactory())
    reactor.run()

    log.startLogging(sys.stdout)

if __name__ == '__main__':
    request = {
        'host' : 'cpctest.com',
        'port' : 8000,
        'cmd' : 'put',
        'local_file_path' : '/tmp/cpc_test/client/client_send'
    }
    file_transaction(request)

    # request = {
    #     'host' : 'cpctest.com',
    #     'port' : 8000,
    #     'cmd' : 'get',
    #     'remote_file_path' : 'server_send',
    #     'local_file_path' : '/tmp/cpc_test/client/client_received'
    # }
    # file_transaction(request)

    # request = {
    #     'host' : 'cpctest.com',
    #     'port' : 8000,
    #     'cmd' : 'list'
    #     }
    # file_transaction(request)
    # if 'file_list' in request:
    #     print(request['file_list'])
