import sys, os, json
import importlib

from signal import signal, SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM
from random import randint

from twisted.internet.defer import DeferredList, inlineCallbacks

from cpchain.utils import reactor, join_with_rc, config

from cpchain.crypto import ECCipher
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.client import pick_proxy, start_proxy_request, download_proxy_file

from cpchain.stress.account import create_test_accounts

order_id = 0

class Player:

    def __init__(self, eth_account):
        self.private_key = ECCipher.create_private_key(eth_account.privateKey)
        public_key = ECCipher.create_public_key_from_private_key(self.private_key)
        self.public_key = ECCipher.serialize_public_key(public_key)
        # self.addr = eth_account.address
        self.addr = ECCipher.get_address_from_public_key(public_key)

    @inlineCallbacks
    def upload_data(self, storage_type, file_path):

        storage_plugin = "cpchain.storage_plugin."
        module = importlib.import_module(storage_plugin + storage_type)
        s = module.Storage()
        data_type = s.data_type

        param = yield s.user_input_param()
        param['proxy_id'] = param['proxy_id'][0] # should be selected by UI

        storage_path = yield s.upload_data(file_path, param)

        return {
            'type': storage_type,
            'path': storage_path,
            'data_type': data_type
        }

    @inlineCallbacks
    def mockup_order(self, storage, buyer):
        global order_id

        proxy_list = yield pick_proxy()
        proxy_id = proxy_list[0]

        if not proxy_id:
            return

        order_id += 1

        return {
            'order_id': order_id,
            'order_type': storage['data_type'],
            'storage_type': storage['type'],
            'storage_path': storage['path'],
            'seller': self.addr,
            'buyer': buyer.addr,
            'proxy': proxy_id,
            'market_hash': 'MARKET_HASH',
            'AES_key': b'AES_key'
        }

    @inlineCallbacks
    def send_seller_message(self, order):

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

        proxy_id = order['proxy']

        error, AES_key, urls = yield start_proxy_request(sign_message, proxy_id)

        if error:
            print(error)
        else:
            print(AES_key)
            print(urls)

    @inlineCallbacks
    def send_buyer_message(self, order):

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

        proxy_id = order['proxy']

        error, AES_key, urls = yield start_proxy_request(sign_message, proxy_id)

        if error:
            print(error)
        else:
            print(AES_key)
            print(urls)
            if order['order_type'] == 'file':
                file_name = urls[0].split('/')[3]
                file_dir = join_with_rc(config.wallet.download_dir)
                # create if not exists
                os.makedirs(file_dir, exist_ok=True)
                file_path = os.path.join(file_dir, file_name)

                yield download_proxy_file(urls[0], file_path)

players = {}

@inlineCallbacks
def job_loop(loop_num, accounts):

    test_players = []
    for account in accounts:
        if account in players:
            player = players[account]
        else:
            player = Player(account)
            players[account] = player

        test_players.append(player)

    seller = test_players[0]
    buyer = test_players[1]

    while loop_num:
        yield do_one_order(seller, buyer)
        loop_num -= 1


@inlineCallbacks
def do_one_order(seller, buyer):
    storage = yield seller.upload_data('proxy', '/bin/bash')

    order = yield seller.mockup_order(storage, buyer)

    yield seller.send_seller_message(order)

    yield buyer.send_buyer_message(order)

def signal_handler(*args):
    sys.exit(1)

def install_signal():
    for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
        signal(sig, signal_handler)

@inlineCallbacks
def main():
    install_signal()

    account_num = 10
    concurrence_num = 1
    loop_num = 1

    ds = []

    accounts = yield create_test_accounts(account_num)

    while concurrence_num:
        test_accounts = []
        for i in range(0, 2):
            account = accounts[randint(0, account_num - 1)]
            test_accounts.append(account)

        d = job_loop(loop_num, test_accounts)
        ds.append(d)

        concurrence_num -= 1

    def handle_result(result):
        success_num = 0
        failure_num = 0
        for (success, value) in result:
            if success:
                success_num += 1
            else:
                print('job failure with exception: %s' % value.getErrorMessage())
                failure_num += 1

        print('job stat: %d succeed, %d failed.' % (success_num, failure_num))

    if ds:
        dl = DeferredList(ds, consumeErrors=True)
        dl.addCallback(handle_result)


if __name__ == '__main__':

    from twisted.python import log

    log.startLogging(sys.stdout)

    main()

    reactor.run()
