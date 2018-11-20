import sys
import time
from signal import signal, SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM
from random import randint
from threading import current_thread

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from twisted.internet.threads import deferToThread
from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred

from cpchain.utils import reactor, config, join_with_root
from cpchain.crypto import Encoder

from cpchain.chain.utils import default_w3 as w3
from cpchain.chain.agents import BuyerAgent, SellerAgent, ProxyAgent

from cpchain.chain.models import OrderInfo

from cpchain.stress.account import create_test_accounts, _passphrase
from cpchain.stress.debug import functrace

@functrace
def generate_rsa_public_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
        )
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    return public_key

class Player:
    contract_path = join_with_root(config.chain.contract_bin_path)
    contract_name = config.chain.contract_name

    def __init__(self, account):
        self.account = account

        self.buyer_agent = BuyerAgent(w3, self.contract_path, self.contract_name, self.account.address)
        self.seller_agent = SellerAgent(w3, self.contract_path, self.contract_name, self.account.address)
        self.proxy_agent = ProxyAgent(w3, self.contract_path, self.contract_name, self.account.address)

        self.rsa_public_key = generate_rsa_public_key()

    @functrace
    def publish_product(self):
        # TODO: get market hash and price from market
        msg_hash = 'fecdef0c'
        desc_hash = Encoder.str_to_base64_byte(msg_hash)

        # TODO: not support 0 and float yet.
        value = randint(1, 100)

        return OrderInfo(
            desc_hash=desc_hash,
            seller=self.account.address,
            value=value,

            buyer_rsa_pubkey=None,
            proxy=None,
            secondary_proxy=None,
            proxy_value=None,
            time_allowed=None
        )

    @functrace
    def buyer_place_order(self, product, proxy):
        buyer_rsa_pubkey = self.rsa_public_key

        product = OrderInfo(
            desc_hash=product.desc_hash,
            buyer_rsa_pubkey=buyer_rsa_pubkey,
            seller=product.seller,
            proxy=proxy.account.address,
            secondary_proxy=proxy.account.address,
            proxy_value=10,
            value=product.value,
            time_allowed=3600 * 24
        )

        w3.personal.unlockAccount(self.account.address, _passphrase)

        order_id = self.buyer_agent.place_order(product)
        # w3.personal.lockAccount(self.account.address)

        # return -1 if failure
        return order_id

    @functrace
    def seller_confirm_order(self, order_id):
        w3.personal.unlockAccount(self.account.address, _passphrase)
        tx_receipt = self.seller_agent.confirm_order(order_id)
        # w3.personal.lockAccount(self.account.address)

        return tx_receipt

    @functrace
    def proxy_claim_fetched(self, order_id):
        w3.personal.unlockAccount(self.account.address, _passphrase)
        tx_receipt = self.proxy_agent.claim_fetched(order_id)
        # w3.personal.lockAccount(self.account.address)

        return tx_receipt

    @functrace
    def proxy_claim_delivered(self, order_id):
        w3.personal.unlockAccount(self.account.address, _passphrase)
        tx_receipt = self.proxy_agent.claim_delivered(order_id, b'dummy')
        # w3.personal.lockAccount(self.account.address)

        return tx_receipt

    @functrace
    def buyer_confirm_order(self, order_id):
        w3.personal.unlockAccount(self.account.address, _passphrase)
        tx_receipt = self.buyer_agent.confirm_order(order_id)
        # w3.personal.lockAccount(self.account.address)

        return tx_receipt


players = {}

@functrace
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
    proxy = test_players[2]

    while loop_num:
        success = do_one_order(seller, buyer, proxy)
        if not success:
            print('failure order flow: seller %s, buyer %s, proxy %s' % (
                seller.account.address, buyer.account.address, proxy.account.address)
                )
            break
        else:
            print('success order flow: seller %s, buyer %s, proxy %s' % (
                seller.account.address, buyer.account.address, proxy.account.address)
                )

        loop_num -= 1

    return success

@functrace
def do_one_order(seller, buyer, proxy):

    product = seller.publish_product()
    order_id = buyer.buyer_place_order(product, proxy)
    if order_id < 0:
        print('buyer %s failed to place order!' % buyer.account.address)
        return False
    tx_receipt = seller.seller_confirm_order(order_id)
    if tx_receipt.status == 0:
        print('seller %s failed to confirm order' % seller.account.address)
        print(tx_receipt)
        return False
    tx_receipt = proxy.proxy_claim_fetched(order_id)
    if tx_receipt.status == 0:
        print('proxy %s failed to claim fetched' % proxy.account.address)
        print(tx_receipt)
        return False
    tx_receipt = proxy.proxy_claim_delivered(order_id)
    if tx_receipt.status == 0:
        print('proxy %s failed to claim delivered' % proxy.account.address)
        print(tx_receipt)
        return False
    tx_receipt = buyer.buyer_confirm_order(order_id)
    if tx_receipt.status == 0:
        print('buyer %s failed to confirm order' % buyer.account)
        print(tx_receipt)
        return False
    return True

def signal_handler(*args):
    sys.exit(1)

def install_signal():
    for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
        signal(sig, signal_handler)

@inlineCallbacks
def main():
    install_signal()

    account_num = 100
    concurrence_num = 100
    loop_num = 10

    ds = []

    accounts = yield create_test_accounts(account_num)

    while concurrence_num:
        test_accounts = []
        for i in range(0, 3):
            account = accounts[randint(0, account_num - 1)]
            test_accounts.append(account)

        d = deferToThread(job_loop, loop_num, test_accounts)
        ds.append(d)

        concurrence_num -= 1

    def handle_result(result):
        success_num = 0
        failure_num = 0
        for (success, value) in result:
            if success:
                if value:
                    success_num += 1
                else:
                    failure_num += 1
            else:
                print('job failure with exception: %s' % value.getErrorMessage())
                failure_num += 1

        print('job stat: %d succeed, %d failed.' % (success_num, failure_num))

    if ds:
        dl = DeferredList(ds, consumeErrors=True)
        dl.addCallback(handle_result)

if __name__ == '__main__':

    main()

    reactor.run()
