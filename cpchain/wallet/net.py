import logging

import treq
from twisted.internet.defer import inlineCallbacks

from cpchain.crypto import ECCipher

from cpchain.utils import config, Encoder

from cpchain.wallet.fs import publish_file_update

logger = logging.getLogger(__name__)  # pylint: disable=locally-disabled, invalid-name


class MarketClient:
    def __init__(self, wallet):
        self.wallet = wallet
        self.account = self.wallet.accounts.default_account
        self.public_key = ECCipher.serialize_public_key(self.account.public_key)
        self.url = config.market.market_url_test
        # private_key_file_path = join_with_root(config.wallet.private_key_file)
        # password_path = join_with_root(config.wallet.private_key_password_file)
        # with open(password_path) as f:
        #     password = f.read()
        self.token = ''
        self.nonce = ''


    @staticmethod
    def str_to_timestamp(s):
        return s


    @inlineCallbacks
    def login(self):
        header = {'Content-Type': 'application/json'}
        data = {'public_key': self.public_key}
        resp = yield treq.post(url=self.url + 'account/v1/login/', headers=header, json=data,
                               persistent=False)
        confirm_info = yield treq.json_content(resp)
        logger.debug("login response: %s", confirm_info)
        self.nonce = confirm_info['message']
        logger.debug('nonce: %s', self.nonce)
        signature = ECCipher.create_signature(self.account.private_key, self.nonce)
        header_confirm = {'Content-Type': 'application/json'}
        data_confirm = {'public_key': self.public_key, 'code': Encoder.bytes_to_hex(signature)}
        resp = yield treq.post(self.url + 'account/v1/confirm/', headers=header_confirm,
                               json=data_confirm,
                               persistent=False)
        confirm_info = yield treq.json_content(resp)
        logger.debug('login confirm: %s', confirm_info)
        self.token = confirm_info['message']
        logger.debug('token: %s', self.token)
        if confirm_info['status'] == 1:
            logger.debug("login succeed")
        return confirm_info['status']


    @inlineCallbacks
    def publish_product(self, selected_id, title, description, price, tags, start_date, end_date,
                        file_md5):
        logger.debug("start publish product")
        header = {'Content-Type': 'application/json'}
        header['MARKET-KEY'] = self.public_key
        header['MARKET-TOKEN'] = self.token
        logger.debug('header token: %s', self.token)
        data = {'owner_address': self.public_key, 'title': title, 'description': description,
                'price': price, 'tags': tags, 'start_date': start_date, 'end_date': end_date,
                'file_md5': file_md5}
        signature_source = str(self.public_key) + str(title) + str(description) + str(
            price) + MarketClient.str_to_timestamp(start_date) + MarketClient.str_to_timestamp(
            end_date) + str(file_md5)
        signature = ECCipher.create_signature(self.account.private_key, signature_source)
        data['signature'] = Encoder.bytes_to_hex(signature)
        logger.debug("signature: %s", data['signature'])
        resp = yield treq.post(self.url + 'product/v1/product/publish/', headers=header, json=data, persistent=False)
        confirm_info = yield treq.json_content(resp)
        print(confirm_info)
        logger.debug('market_hash: %s', confirm_info['data']['market_hash'])
        market_hash = confirm_info['data']['market_hash']
        publish_file_update(market_hash, selected_id)
        return market_hash


    # @inlineCallbacks
    # def change_product_status(self, status):
    #     header = {'Content-Type': 'application/json', 'MARKET-KEY': self.account.pub_key,
    #               'MARKET-TOKEN': self.token}
    #     data = {'status': status}
    #     resp = yield treq.post(url=self.url+'product_change', headers=header, json=data)
    #     confirm_info = yield treq.json_content(response=resp)
    #     if not confirm_info['success']:
    #         print('publish failed')


    @inlineCallbacks
    def query_product(self, keyword):
        header = {'Content-Type': 'application/json'}
        url = self.url + 'product/v1/es_product/search/?keyword=' + str(keyword)
        resp = yield treq.get(url=url, headers=header)
        confirm_info = yield treq.json_content(resp)
        logger.debug("query product confirm info: %s", confirm_info)
        return confirm_info['results']


    @inlineCallbacks
    def query_by_tag(self, tag):
        url = self.url + 'product/v1/es_product/search/?status=0&tag=' + str(tag)
        header = header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        resp = yield treq.get(url, headers=header)
        confirm_info = yield treq.json_content(resp)
        logger.debug('query by tag confirm info: %s', confirm_info)
        return confirm_info['results']


    # @inlineCallbacks
    # def query_by_tag(self, tag):
    #     header = {'Content-Type': 'application/json'}
    #     url = self.url + 'product/search/?keyword=[' + str(tag) + ']'
    #     resp = yield treq.get(url=url, headers=header)
    #     confirm_info = yield treq.json_content(resp)
    #     print('product info: ')
    #     print(confirm_info)
    #     return confirm_info


    # @inlineCallbacks
    # def logout(self):
    #     header = {'Content-Type': 'application/json', 'MARKET-KEY': self.account.pub_key,
    #               'MARKET-TOKEN': self.token}
    #     data = {'public_key': self.account.pub_key, 'token': self.token}
    #     resp = yield treq.post(url=self.url+'logout', headers=header, json=data)
    #     confirm_info = yield treq.json_content(resp)
    #     print(confirm_info)


    @inlineCallbacks
    def query_carousel(self):
        # try:
        logger.debug('status: in query carousel')
        url = self.url + 'main/v1/carousel/list/'
        logger.debug("query carousel url: %s", url)
        header = {'Content-Type': 'application/json', 'MARKET-KEY': self.public_key,
                  'MARKET-TOKEN': self.token}
        resp = yield treq.get(url=url, headers=header)
        # logger.debug("response:", resp)
        confirm_info = yield treq.json_content(resp)
        print(confirm_info)
        logger.debug("carousel response: %s", confirm_info)
        # except Exception as err:
        #     logger.debug(err)
        return confirm_info['data']


    @inlineCallbacks
    def query_hot_tag(self):
        url = self.url + 'main/v1/hot_tag/list/'
        header = {'Content-Type': 'application/json', 'MARKET-KEY': self.public_key,
                  'MARKET-TOKEN': self.token}
        resp = yield treq.get(url=url, headers=header)
        confirm_info = yield treq.json_content(resp)
        print(confirm_info)
        logger.debug("hot tag: %s", confirm_info)
        return confirm_info['data']


    @inlineCallbacks
    def query_promotion(self):
        url = self.url + 'main/v1/promotion/list/'
        header = {'Content-Type': 'application/json', 'MARKET-KEY': self.public_key,
                  'MARKET-TOKEN': self.token}
        resp = yield treq.get(url=url, headers=header)
        confirm_info = yield treq.json_content(resp)
        print(confirm_info)
        logger.debug("promotion: %s", confirm_info)
        return confirm_info['data']


    @inlineCallbacks
    def query_recommend_product(self):
        url = self.url + 'product/v1/recommend_product/list/'
        header = {'Content-Type': 'application/json', 'MARKET-KEY': self.public_key,
                  'MARKET-TOKEN': self.token}
        resp = yield treq.get(url=url, headers=header)
        confirm_info = yield treq.json_content(resp)
        print(confirm_info)
        logger.debug("recommend product: %s", confirm_info)
        return confirm_info['data']


    @inlineCallbacks
    def add_product_sales_quantity(self, market_hash):
        url = self.url + '/product/v1/product/sales_quantity/add/'
        payload = {'market_hash': market_hash}
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        resp = yield treq.post(url, headers=header, json=payload)
        confirm_info = yield treq.json_content(resp)
        return confirm_info


    @inlineCallbacks
    def subscribe_tag(self, tag):
        url = self.url + '/product/v1/product/tag/subscribe/'
        payload = {'public_key': self.public_key, 'tag': tag}
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        resp = yield treq.post(url, headers=header, json=payload)
        confirm_info = yield treq.json_content(resp)
        return confirm_info['status']


    @inlineCallbacks
    def unsubscribe_tag(self, tag):
        url = self.url + '/product/v1/product/tag/unsubscribe/'
        payload = {'public_key': self.public_key, 'tag': tag}
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        resp = yield treq.post(url, headers=header, json=payload)
        confirm_info = yield treq.json_content(resp)
        return confirm_info['status']


    @inlineCallbacks
    def subscribe_seller(self, seller_pub_key):
        url = self.url + '/product/v1/product/seller/subscribe/'
        payload = {'public_key': self.public_key, 'seller_public_key': seller_pub_key}
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        resp = yield treq.post(url, headers=header, json=payload)
        confirm_info = yield treq.json_content(resp)
        return confirm_info['status']


    @inlineCallbacks
    def unsubscribe_seller(self, seller_pub_key):
        url = self.url + '/product/v1/product/seller/unsubscribe/'
        payload = {'public_key': self.public_key, 'seller_public_key': seller_pub_key}
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        resp = yield treq.post(url, headers=header, json=payload)
        confirm_info = yield treq.json_content(resp)
        return confirm_info['status']


    @inlineCallbacks
    def query_by_subscribe_seller(self):
        url = self.url + '/product/v1/product/seller/search/'
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        resp = yield treq.get(url, headers=header)
        confirm_info = yield treq.json_content(resp)
        return confirm_info['status']


    @inlineCallbacks
    def query_by_subscribe_tag(self):
        url = self.url + '/product/v1/product/tag/search/'
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        resp = yield treq.get(url, headers=header)
        confirm_info = yield treq.json_content(resp)
        return confirm_info['status']


    @inlineCallbacks
    def upload_file_info(self, hashcode, path, size, product_id, remote_type, remote_uri, aes_key, name):
        logger.debug("upload file info to market")
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        data = {"public_key": self.public_key,
                   "hashcode": hashcode, "path": path, "size": size, "client_id": product_id,
                   "remote_type": remote_type, "remote_uri": remote_uri, "is_published": "False",
                   "aes_key": 'encrypted-aes-key', "market_hash": "hash", "name": name}
        url = self.url + 'user_data/v1/uploaded_file/add/'
        logger.debug('upload file info payload: %s', data)
        logger.debug('upload file info url: %s', url)
        resp = yield treq.post(url, headers=header, json=data, persistent=False)
        confirm_info = yield treq.json_content(resp)
        logger.debug('upload file info to market: %s', confirm_info)
        return confirm_info['status']


    @inlineCallbacks
    def update_file_info(self, product_id, market_hash):
        logger.debug("update file info in market")
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        data = {"client_id": product_id, "market_hash": market_hash, "is_published": True}
        url = self.url + 'user_data/v1/uploaded_file/update/'
        logger.debug('upload file info payload: %s', data)
        logger.debug('upload file info url: %s', url)
        logger.debug('product id: %s', product_id)
        resp = yield treq.post(url, headers=header, json=data, persistent=False)
        confirm_info = yield treq.json_content(resp)
        logger.debug('upload file info to market confirm: %s', confirm_info)
        return confirm_info['status']
