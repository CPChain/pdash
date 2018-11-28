import time

from hashlib import sha1
from random import randint

from twisted.internet.threads import deferToThread
from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred

from cpchain.utils import reactor, Encoder

from cpchain.stress.chain import Player as Chain
from cpchain.stress.proxy import Player as Proxy
from cpchain.stress.market import Player as Market
from cpchain.stress.utils import random_id


class Player:
    def __init__(self, eth_account):
        self.address = eth_account.address

        self.market = Market(eth_account)
        self.proxy = Proxy(eth_account)
        self.chain = Chain(eth_account)


def eth_addr_to_string(eth_addr):
    string_addr = eth_addr[2:]
    string_addr = string_addr.lower()
    return string_addr

@inlineCallbacks
def do_one_order(seller, buyer, _):

    status = yield seller.market.login()
    if not status:
        print('seller %s failed to login' % seller.address)
        return False

    status = yield buyer.market.login()
    if not status:
        print('buyer %s failed to login' % buyer.address)
        return False

    storage = yield seller.proxy.upload_data('proxy', '/bin/bash')

    seller.market.product_id += 1
    product_id = seller.market.product_id

    status = yield seller.market.upload_file_info(product_id, storage['type'], storage['path'])
    if not status:
        print('seller %s failed to upload file info' % seller.address)
        return False

    product_title = 'stress testing product %s' % random_id()
    market_hash = yield seller.market.publish_product(product_title, 'file')
    if not market_hash:
        print('seller %s failed to publish product %s' % (seller.address, product_title))
        return False

    status = yield seller.market.update_file_info(product_id, market_hash)
    if not status:
        print('seller %s failed to update file info %d with hash %s' % (seller.address, product_id, market_hash))
        return False

    order = {}

    product_info_list = yield buyer.market.products(product_title)
    if not product_info_list:
        print('buyer %s failed to query product with title %s' % (buyer.address, product_title))
        return False
    else:
        product = product_info_list[0]
        order['order_type'] = product['ptype']

    proxy_id = yield buyer.proxy.pick_proxy()
    if not proxy_id:
        print('buyer %s failed to pick proxy' % buyer.address)
        return False

    order_id = yield buyer.chain.buyer_place_order(product, proxy_id)
    if order_id < 0:
        print('buyer %s failed to place order!' % buyer.address)
        return False

    status = seller.chain.seller_confirm_order(order_id)
    if status == 0:
        print('seller %s failed to confirm order' % seller.address)
        return False

    order_record = seller.chain.query_order(order_id)
    if not order_record:
        print('seller %s failed to query order %d' % (seller.address, order_id))
        return False
    else:
        order['order_id'] = order_id
        order['market_hash'] = Encoder.bytes_to_base64_str(order_record[0])
        order['seller'] = eth_addr_to_string(order_record[3])
        order['buyer'] = eth_addr_to_string(order_record[2])
        # buyer_rsa_public_key = order_record[1]
        order['proxy'] = eth_addr_to_string(order_record[4])

    order['AES_key'] = b'AES_key'  # fake AES Key

    data_info = yield seller.market.query_data(market_hash)
    if not data_info:
        print('seller %s failed to query data with hash %s' % (seller.address, market_hash))
        return False
    else:
        order['storage_type'] = data_info['remote_type']
        order['storage_path'] = data_info['remote_uri']

    yield seller.proxy.send_seller_message(order)       # proxy would claim data fetched on receiving seller's request

    yield buyer.proxy.send_buyer_message(order)     # proxy would claim data delivered on receiving buyer's request

    status = buyer.chain.buyer_confirm_order(order_id)
    if status == 0:
        print('buyer %s failed to confirm order' % buyer.address)
        return False

    # status = yield buyer.market.add_comment_by_hash(market_hash, comment="stress testing comment")  # not working
    # if not status:
    #     print('buyer failed to add comment for product market hash %s' % market_hash)
    #     return False
    # comment = yield seller.market.query_comment_by_hash(market_hash)                 # not working
    # if not comment:
    #     print('seller failed to query comment for product market hash %s' % market_hash)
    #     return False

    resp = yield buyer.market.add_product_sales_quantity(market_hash)
    if not resp['status']:
        print('buyer failed to add sales quantity for product market hash %s' % market_hash)
        return False

    return True


if __name__ == '__main__':

    from cpchain.stress.utils import run_jobs

    run_jobs(Player, do_one_order, 10, 1, 1)

    reactor.run()
