import logging
import requests
import treq

from datetime import datetime, timedelta
from random import randint

from twisted.internet.defer import inlineCallbacks

from cpchain.utils import reactor, config, Encoder, join_with_root
from cpchain.wallet.net import MarketClient
from cpchain.wallet.utils import build_url
from cpchain.account import Account

from cpchain.stress.account import _passphrase
from cpchain.stress.utils import random_id

logger = logging.getLogger(__name__)

class Player(MarketClient):
    def __init__(self, account):
        self.address = account.address

        super().__init__(wallet=None, account=Account(private_key=account.privateKey))

        self.product_id = 0

        self.selected_id = 0

    @inlineCallbacks
    def login(self):
        resp = yield self.query_username()

        if not resp['username']:
            username = 'stress tester ' + self.address
        else:
            username = resp['username']

        status = yield super().login(username)
        return status

    def upload_file_info(self, product_id, remote_type=None, remote_uri=None):

        hashcode = 'stress testing data hash'
        path = 'stress testing data path'
        size = 1234
        remote_type = remote_type or 'stress testing remote type'
        remote_uri = remote_uri or 'stress testing remote uri'
        name = 'stress testing name'
        encrypted_key = 'stress testing encrypted key'
        return super().upload_file_info(hashcode, path, size, product_id, remote_type, remote_uri, name, encrypted_key)

    def publish_product(self, title, ptype=None):

        if not ptype:
            type_list = ['file', 'stream']
            ptype = type_list[randint(0,1)]
        description = 'stress testing description'
        price = randint(1, 10000) * 0.01   # could not be zero now.
        tags = 'stress testing tags'
        now = datetime.now()
        start_date = now.isoformat()
        end_date = (now + timedelta(days=7)).isoformat()
        category = 'stress testing category'
        cover_image = join_with_root('cpchain/assets/wallet/icons/logo@2x.png')

        self.selected_id +=  1

        return super().publish_product(self.selected_id, title, ptype, description, str(price),
                tags, start_date, end_date, category, cover_image)


@inlineCallbacks
def do_one_order(seller, buyer, _):

    status = yield seller.login()
    if not status:
        print('seller %s failed to login' % seller.address)
        return False
    status = yield buyer.login()
    if not status:
        print('buyer %s failed to login' % buyer.address)
        return False

    seller.product_id += 1
    product_id = seller.product_id

    status = yield seller.upload_file_info(product_id)
    if not status:
        print('seller %s failed to upload file info' % seller.address)
        return False

    product_title = 'stress testing product %s' % random_id()
    market_hash = yield seller.publish_product(product_title)
    if not market_hash:
        print('seller %s failed to publish product %s' % (seller.address, product_title))
        return False

    status = yield seller.update_file_info(product_id, market_hash)
    if not status:
        print('seller %s failed to update file info %d with hash %s' % (seller.address, product_id, market_hash))
        return False

    # product_info_list = yield player.query_product('stress testing title 7') # not working
    # print(product_info_list)
    # result = yield player.query_by_seller(player.public_key) # not working
    # print(result)

    data_info = yield seller.query_data(market_hash)
    if not data_info:
        print('seller %s failed to query data with hash %s' % (seller.address, market_hash))
        return False

    product_info_list = yield buyer.products(product_title)
    if not product_info_list:
        print('buyer %s failed to query product with title %s' % (seller.address, product_title))
        return False

    product_info_list = yield seller.myproducts()
    if not product_info_list:
        print('seller %s failed to get product list' % seller.address)
        return False

    # resp = yield buyer.add_product_sales_quantity(market_hash)
    # if not resp['status']:
    #     print('seller %s failed to add product sales quantity with hash %s' % (seller.address, market_hash))
    #     return False

    # data_info = yield player.query_records(seller.address)
    # if not data_info:
    #     return False
    # status = yield buyer.add_comment_by_hash(market_hash, comment="stress testing comment") # not working
    # if not status:
    #     return False
    # comment = yield seller.query_comment_by_hash(market_hash)        # not working
    # if not comment:
    #     return False

    status = yield seller.delete_file_info(product_id)
    if not status:
        print('seller %s failed to delete file info %d' % (seller.address, product_id))
        return False

    return True

if __name__ == '__main__':

    from cpchain.stress.utils import run_jobs

    run_jobs(Player, do_one_order, 10, 1, 1)

    reactor.run()
