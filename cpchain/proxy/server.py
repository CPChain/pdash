#!/usr/bin/env python3

import os
import json
import logging
import importlib

from uuid import uuid1 as uuid

from twisted.internet import threads, protocol, ssl
from twisted.protocols.basic import NetstringReceiver

from cpchain import config
from cpchain.utils import join_with_rc, join_with_root
from cpchain.utils import reactor

from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.message import message_sanity_check, \
sign_message_verify, is_address_from_key

from cpchain.proxy.db import Trade, ProxyDB

from cpchain.proxy.chain import order_is_ready_on_chain, \
claim_data_delivered_to_chain, claim_data_fetched_to_chain

logger = logging.getLogger(__name__)


class SSLServerProtocol(NetstringReceiver):

    def connectionMade(self):
        self.peer = self.transport.getPeer()
        logger.debug("connect to client %s" % str(self.peer))

    def stringReceived(self, string):
        sign_message = SignMessage()
        sign_message.ParseFromString(string)

        valid = sign_message_verify(sign_message)

        if not valid:
            error = 'wrong signature'
            return self.proxy_reply_error(error)

        message = Message()
        message.ParseFromString(sign_message.data)
        valid = message_sanity_check(message)
        if not valid or message.type == Message.PROXY_REPLY:
            error = "wrong client request"
            return self.proxy_reply_error(error)

        public_key = sign_message.public_key

        if message.type == Message.SELLER_DATA:
            public_addr = message.seller_data.seller_addr
        elif message.type == Message.BUYER_DATA:
            public_addr = message.buyer_data.buyer_addr

        if not is_address_from_key(public_addr, public_key):
            error = "public key does not match with address"
            return self.proxy_reply_error(error)

        self.handle_message(message)

    def handle_message(self, message):

        proxy_db = self.proxy_db
        trade = Trade()

        if message.type == Message.SELLER_DATA:
            data = message.seller_data
            trade.order_id = data.order_id
            trade.order_type = data.order_type
            trade.seller_addr = data.seller_addr
            trade.buyer_addr = data.buyer_addr
            trade.market_hash = data.market_hash

            if proxy_db.query(trade):
                error = "trade record already in database"
                return self.proxy_reply_error(error)

            if not order_is_ready_on_chain(trade.order_id):
                error = "order is not ready on chain"
                return self.proxy_reply_error(error)

            trade.AES_key = data.AES_key
            trade.order_delivered = False

            # to avoid conflict, use uuid as local file path for file type order,
            # use uuid as stream id for stream type order.
            trade.data_path = str(uuid())

            if trade.order_type == 'file':
                server_root = join_with_rc(config.proxy.server_root)
                file_path = os.path.join(server_root, trade.data_path)

                storage_type = data.storage.type
                file_uri = data.storage.file_uri

                def download_file():
                    try:
                        storage_module = importlib.import_module(
                            "cpchain.storage-plugin." + storage_type
                            )

                        storage = storage_module.Storage()

                        storage.download_file(
                            file_uri,
                            file_path
                            )

                    except:
                        logger.exception('failed to fetch file')
                        return False
                    else:
                        return True

                d = threads.deferToThread(
                    download_file
                )

                d.addCallback(self.fetch_data_finished, trade)
            elif trade.order_type == 'stream':
                self.fetch_data_finished(True, trade)

        elif message.type == Message.BUYER_DATA:
            data = message.buyer_data
            trade.order_id = data.order_id
            trade.order_type = data.order_type
            trade.seller_addr = data.seller_addr
            trade.buyer_addr = data.buyer_addr
            trade.market_hash = data.market_hash

            trade = proxy_db.query(trade)
            if trade:

                if trade.order_delivered:
                    self.proxy_reply_success(trade)
                elif not claim_data_delivered_to_chain(trade.order_id):
                    error = "failed to claim data delivered to chain"
                    self.proxy_reply_error(error)
                else:
                    trade.order_delivered = True
                    proxy_db.update()
                    self.proxy_reply_success(trade)
            else:
                error = "trade record not found in database"
                self.proxy_reply_error(error)

    def fetch_data_finished(self, success, trade):
        if success:
            if not claim_data_fetched_to_chain(trade.order_id):
                error = "failed to claim data fetched to chain"
                self.proxy_reply_error(error)
            else:
                self.proxy_db.insert(trade)
                self.proxy_reply_success(trade)
        else:
            error = "failed to download file"
            self.proxy_reply_error(error)

    def proxy_reply_success(self, trade):
        message = Message()
        message.type = Message.PROXY_REPLY
        proxy_reply = message.proxy_reply
        proxy_reply.AES_key = trade.AES_key
        if trade.order_type == 'file':
            proxy_reply.port_conf = json.dumps({'file': self.port_conf['file']})
        elif trade.order_type == 'stream':
            proxy_reply.port_conf = json.dumps(
                {
                    'stream_ws': self.port_conf['stream_ws'],
                    'stream_restful': self.port_conf['stream_restful']

                }
                )
        proxy_reply.data_path = trade.data_path

        string = message.SerializeToString()
        self.sendString(string)
        self.transport.loseConnection()

    def proxy_reply_error(self, error):
        message = Message()
        message.type = Message.PROXY_REPLY
        proxy_reply = message.proxy_reply
        proxy_reply.error = error
        string = message.SerializeToString()
        self.sendString(string)
        self.transport.loseConnection()

    def connectionLost(self, reason):
        logger.debug("lost connection to client %s" % str(self.peer))


class ProxyServer:
    def __init__(self):
        self.trans = None

        self.factory = protocol.Factory()
        self.factory.protocol = SSLServerProtocol
        self.factory.protocol.proxy_db = ProxyDB()
        self.factory.protocol.port_conf = {
            'file': config.proxy.server_file_port,
            'stream_ws': config.proxy.server_stream_ws_port,
            'stream_restful': config.proxy.server_stream_restful_port
        }

        self.port = config.proxy.server_port

        server_root = join_with_rc(config.proxy.server_root)
        server_root = os.path.expanduser(server_root)
        os.makedirs(server_root, exist_ok=True)

    def run(self):
        server_key = os.path.expanduser(
            join_with_rc(config.proxy.server_key))
        server_crt = os.path.expanduser(
            join_with_rc(config.proxy.server_crt))

        if not os.path.isfile(server_key):
            logger.info("SSL key/cert file not found, "
                        + "run local self-test by default")
            server_key_sample = 'cpchain/assets/proxy/key/server.key'
            server_crt_sample = 'cpchain/assets/proxy/key/server.crt'
            server_key = join_with_root(server_key_sample)
            server_crt = join_with_root(server_crt_sample)

        self.trans = reactor.listenSSL(
            self.port,
            self.factory,
            ssl.DefaultOpenSSLContextFactory(
                server_key,
                server_crt
                )
            )

    def stop(self):
        self.trans.stopListening()
