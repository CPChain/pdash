import time
from random import randint

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from cpchain.utils import reactor, config, join_with_root
from cpchain.crypto import Encoder, ECCipher

from cpchain.chain.utils import default_w3 as w3
from cpchain.chain.agents import BuyerAgent, SellerAgent, ProxyAgent

from cpchain.chain.models import OrderInfo

from cpchain.stress.account import _passphrase

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
        self.address = account.address
        self.account = account

        self.buyer_agent = BuyerAgent(w3, self.contract_path, self.contract_name, self.address)
        self.seller_agent = SellerAgent(w3, self.contract_path, self.contract_name, self.address)
        self.proxy_agent = ProxyAgent(w3, self.contract_path, self.contract_name, self.address)

        self.rsa_public_key = generate_rsa_public_key()

    def query_order(self, order_id):
        return self.seller_agent.query_order(order_id)

    def mockup_product(self):
        private_key = ECCipher.create_private_key(self.account .privateKey)
        public_key = ECCipher.create_public_key_from_private_key(private_key)
        public_key = ECCipher.serialize_public_key(public_key)

        price = randint(1, 10000) * 0.01
        return {
            'description': 'stress testing description',
            'signature': '304502201b31544ff65ebbfff3743a0b2536388e1f6cf2533de4bbf0ffab57d762f54d50022100a8101face8c6a6d2f0e01a9a01ea49d80598c880872db9e3c1e9eb27a23a2554',
            'cover_image': 'upload_images/20181127072441_13.png',
            'end_date': '2018-12-04T15:24:41.664517Z',
            'msg_hash': 'dRFWYcWC9TKujDo7mLiUCq00MthHezzkyncAGIdaEos=',
            'id': 53,
            'start_date': '2018-11-27T15:24:41.664517Z',
            'ptype': 'file',
            'seq': 0,
            'owner_address': public_key,
            'tags': 'stress testing tags',
            'price': price,
            'title': 'stress testing product',
            'category': 'stress testing category',
            'status': 0,
            'created': '2018-11-27T07:24:41.715315Z'
        }

    def buyer_place_order(self, product, proxy):
        buyer_rsa_pubkey = self.rsa_public_key

        desc_hash = Encoder.str_to_base64_byte(product['msg_hash'])

        public_key = ECCipher.create_public_key(Encoder.hex_to_bytes(product['owner_address']))
        seller_addr = w3.toChecksumAddress(ECCipher.get_address_from_public_key(public_key))
        proxy = w3.toChecksumAddress(proxy)

        product = OrderInfo(
            desc_hash=desc_hash,
            buyer_rsa_pubkey=buyer_rsa_pubkey,
            seller=seller_addr,
            proxy=proxy,
            secondary_proxy=proxy,
            proxy_value=100,
            value=product['price'],
            time_allowed=3600 * 24
        )

        w3.personal.unlockAccount(self.account.address, _passphrase)

        order_id = self.buyer_agent.place_order(product)
        # w3.personal.lockAccount(self.account.address)

        # return -1 if failure
        return order_id

    def seller_confirm_order(self, order_id):
        w3.personal.unlockAccount(self.account.address, _passphrase)
        status = self.seller_agent.confirm_order(order_id)
        # w3.personal.lockAccount(self.account.address)

        return status

    def proxy_claim_fetched(self, order_id):
        w3.personal.unlockAccount(self.account.address, _passphrase)
        status = self.proxy_agent.claim_fetched(order_id)
        # w3.personal.lockAccount(self.account.address)

        return status

    def proxy_claim_delivered(self, order_id):
        w3.personal.unlockAccount(self.account.address, _passphrase)
        status = self.proxy_agent.claim_delivered(order_id, b'dummy')
        # w3.personal.lockAccount(self.account.address)

        return status

    def buyer_confirm_order(self, order_id):
        w3.personal.unlockAccount(self.account.address, _passphrase)
        status = self.buyer_agent.confirm_order(order_id)
        # w3.personal.lockAccount(self.account.address)

        return status


def do_one_order(seller, buyer, proxy):

    product = seller.mockup_product()
    order_id = buyer.buyer_place_order(product, proxy.account.address)
    if order_id < 0:
        print('buyer %s failed to place order!' % buyer.account.address)
        return False
    status = seller.seller_confirm_order(order_id)
    if status == 0:
        print('seller %s failed to confirm order' % seller.account.address)
        return False
    status = proxy.proxy_claim_fetched(order_id)
    if status == 0:
        print('proxy %s failed to claim fetched' % proxy.account.address)
        return False
    status = proxy.proxy_claim_delivered(order_id)
    if status == 0:
        print('proxy %s failed to claim delivered' % proxy.account.address)
        return False
    status = buyer.buyer_confirm_order(order_id)
    if status == 0:
        print('buyer %s failed to confirm order' % buyer.account.address)
        return False
    return True

if __name__ == '__main__':

    from cpchain.stress.utils import run_jobs

    run_jobs(Player, do_one_order, 10, 1, 1)

    reactor.run()
