import sys, os, json
import importlib

from random import randint

from twisted.internet.defer import inlineCallbacks

from cpchain.utils import reactor, join_with_rc, config

from cpchain.crypto import ECCipher
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.client import pick_proxy, start_proxy_request, download_proxy_file

order_id = 0
slave_port = 10000
kad_port = 15000

class Player:

    def __init__(self, eth_account):
        self.private_key = ECCipher.create_private_key(eth_account.privateKey)
        public_key = ECCipher.create_public_key_from_private_key(self.private_key)
        self.public_key = ECCipher.serialize_public_key(public_key)
        # self.address = eth_account.address
        self.address = ECCipher.get_address_from_public_key(public_key)

    @inlineCallbacks
    def upload_data(self, storage_type, file_path):
        global slave_port
        global kad_port

        storage_plugin = "cpchain.storage_plugin."
        module = importlib.import_module(storage_plugin + storage_type)
        s = module.Storage()
        data_type = s.data_type

        slave_port += 1
        param = yield s.user_input_param(slave_port)
        param['proxy_id'] = param['proxy_id'][0] # should be selected by UI

        kad_port += 1
        storage_path = yield s.upload_data(file_path, param, kad_port)

        return {
            'type': storage_type,
            'path': storage_path,
            'data_type': data_type
        }

    @inlineCallbacks
    def pick_proxy(self):
        global slave_port

        slave_port += 1
        proxy_list = yield pick_proxy(slave_port)
        proxy_id = proxy_list[0]

        return proxy_id

    @inlineCallbacks
    def mockup_order(self, storage, buyer):
        global order_id
        global slave_port

        slave_port += 1
        proxy_list = yield pick_proxy(slave_port)
        proxy_id = proxy_list[0]

        if not proxy_id:
            return

        order_id += 1

        return {
            'order_id': order_id,
            'order_type': storage['data_type'],
            'storage_type': storage['type'],
            'storage_path': storage['path'],
            'seller': self.address,
            'buyer': buyer.address,
            'proxy': proxy_id,
            'market_hash': 'MARKET_HASH',
            'AES_key': b'AES_key'
        }

    @inlineCallbacks
    def send_seller_message(self, order):
        global kad_port

        message = Message()
        seller_data = message.seller_data
        message.type = Message.SELLER_DATA
        seller_data.order_id = order['order_id']
        seller_data.order_type = order['order_type']
        seller_data.seller_addr = order['seller']
        seller_data.buyer_addr = order['buyer']
        seller_data.market_hash = order['market_hash']
        seller_data.AES_key = order['AES_key']

        storage = seller_data.storage

        storage.type = order['storage_type']
        storage.path = order['storage_path']

        sign_message = SignMessage()
        sign_message.public_key = self.public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.create_signature(
            self.private_key,
            sign_message.data
            )

        kad_port += 1

        proxy_id = order['proxy']

        error, AES_key, urls = yield start_proxy_request(sign_message, proxy_id, kad_port)

        if error:
            print(error)
        else:
            print(urls)

    @inlineCallbacks
    def send_buyer_message(self, order):
        global kad_port

        message = Message()
        buyer_data = message.buyer_data
        message.type = Message.BUYER_DATA
        buyer_data.order_id = order['order_id']
        buyer_data.order_type = order['order_type']
        buyer_data.seller_addr = order['seller']
        buyer_data.buyer_addr = order['buyer']
        buyer_data.market_hash = order['market_hash']

        sign_message = SignMessage()
        sign_message.public_key = self.public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.create_signature(
            self.private_key,
            sign_message.data
            )

        kad_port += 1

        proxy_id = order['proxy']

        error, AES_key, urls = yield start_proxy_request(sign_message, proxy_id, kad_port)

        if error:
            print(error)
        else:
            print(urls)
            if order['order_type'] == 'file':
                file_name = urls[0].split('/')[3]
                file_dir = join_with_rc(config.wallet.download_dir)
                # create if not exists
                os.makedirs(file_dir, exist_ok=True)
                file_path = os.path.join(file_dir, file_name)

                yield download_proxy_file(urls[0], file_path)

@inlineCallbacks
def do_one_order(seller, buyer, _):
    storage = yield seller.upload_data('proxy', '/bin/bash')

    order = yield seller.mockup_order(storage, buyer)

    yield seller.send_seller_message(order)

    yield buyer.send_buyer_message(order)

    return True


if __name__ == '__main__':
    from twisted.python import log

    from cpchain.stress.utils import run_jobs

    log.startLogging(sys.stdout)

    run_jobs(Player, do_one_order, 10, 1, 1)

    reactor.run()
