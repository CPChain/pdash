import logging
import treq

from twisted.internet.defer import inlineCallbacks

from cpchain.crypto import ECCipher

from cpchain.utils import config, Encoder

from cpchain.wallet.fs import publish_file_update
from cpchain.wallet import utils



logger = logging.getLogger(__name__)  # pylint: disable=locally-disabled, invalid-name


class MarketClient:
    def __init__(self, wallet):
        self.wallet = wallet
        self.account = self.wallet.accounts.default_account
        self.public_key = ECCipher.serialize_public_key(self.account.public_key)
        self.url = config.market.market_url_test
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
        self.token = confirm_info['message']
        return confirm_info['status']


    @inlineCallbacks
    def publish_product(self, selected_id, title, description, price, tags, start_date, end_date,
                        file_md5, size):

        logger.debug("start publish product")
        header = {'Content-Type': 'application/json'}
        header['MARKET-KEY'] = self.public_key
        header['MARKET-TOKEN'] = self.token
        logger.debug('header token: %s', self.token)
        data = {'owner_address': self.public_key, 'title': title, 'description': description,
                'price': price, 'tags': tags, 'start_date': start_date, 'end_date': end_date,
                'file_md5': file_md5, 'size': size}
        signature_source = str(self.public_key) + str(title) + str(description) + str(
            price) + MarketClient.str_to_timestamp(start_date) + MarketClient.str_to_timestamp(end_date) + str(file_md5)
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


    @inlineCallbacks
    def query_product(self, keyword):
        logger.debug('keywords: %s', keyword)
        header = {'Content-Type': 'application/json'}
        url = self.url + 'product/v1/es_product/search/?search=' + keyword
        logger.debug('query url: %s', url)
        resp = yield treq.get(url=url, headers=header, persistent=False)
        confirm_info = yield treq.json_content(resp)
        logger.debug("query product confirm info: %s", confirm_info)
        return confirm_info['results']


    @inlineCallbacks
    def query_by_tag(self, tag):
        url = self.url + 'product/v1/es_product/search/?status=0&tag=' + str(tag)
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        resp = yield treq.get(url, headers=header)
        confirm_info = yield treq.json_content(resp)
        logger.debug('query by tag confirm info: %s', confirm_info)
        return confirm_info['results']


    @inlineCallbacks
    def query_carousel(self):
        logger.debug('status: in query carousel')
        url = self.url + 'main/v1/carousel/list/'
        logger.debug("query carousel url: %s", url)
        header = {'Content-Type': 'application/json', 'MARKET-KEY': self.public_key,
                  'MARKET-TOKEN': self.token}
        resp = yield treq.get(url=url, headers=header)
        confirm_info = yield treq.json_content(resp)
        print(confirm_info)
        logger.debug("carousel response: %s", confirm_info)
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
        url = self.url + 'product/v1/recommend_product/list/'
        header = {'Content-Type': 'application/json', 'MARKET-KEY': self.public_key,
                  'MARKET-TOKEN': self.token}
        resp = yield treq.get(url=url, headers=header)
        confirm_info = yield treq.json_content(resp)
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
    def upload_file_info(self, hashcode, path, size, product_id, remote_type, remote_uri, name, encrypted_key):
        # fixme: another argument aes_key should be passed and encrypted
        logger.debug("upload file info to market")
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        data = {"public_key": self.public_key, "hashcode": hashcode, "path": path, "size": size,
                "client_id": product_id,
                "remote_type": remote_type, "remote_uri": remote_uri, "is_published": "False",
                "aes_key": encrypted_key, "market_hash": "hash", "name": name}
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


    @inlineCallbacks
    def query_by_seller(self, public_key):
        logger.debug("in query by seller")
        logger.debug("seller's public key: %s", self.public_key)
        logger.debug("public key used by query: %s", public_key)
        url = self.url + 'product/v1/es_product/search/?ordering=-created&offset=0&limit=100&status=0&seller=' + str(public_key)
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token, 'Content-Type': 'application/json'}
        resp = yield treq.get(url, headers=header, persistent=False)
        confirm_info = yield treq.json_content(resp)
        return confirm_info['results']



    @inlineCallbacks
    def query_comment_by_hash(self, market_hash):
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        url = utils.build_url(self.url + "comment/v1/comment/list/", {'market_hash': market_hash})
        logger.debug(url)
        resp = yield treq.get(url, headers=header)
        logger.debug(resp)
        comment_info = yield treq.json_content(resp)
        logger.debug('upload file info to market confirm: %s', comment_info)
        return comment_info['data']


    @inlineCallbacks
    def add_comment_by_hash(self, market_hash, comment=""):
        comment_address = ECCipher.get_address_from_public_key(self.account.public_key)
        logger.debug(comment_address)
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token, 'Content-Type': 'application/json'}
        data = {'public_key': self.public_key, 'market_hash': market_hash, 'content': comment}
        url = utils.build_url(self.url + "comment/v1/comment/add/", {'market_hash': market_hash})

        resp = yield treq.post(url, headers=header, json=data, persistent=False)
        comment_info = yield treq.json_content(resp)
        logger.debug('upload file info to market confirm: %s', comment_info)
        return comment_info['status']

    @inlineCallbacks
    def delete_file_info(self, product_id):
        logger.debug("delete file info in market")
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        data = {"client_id": product_id}
        url = self.url + 'user_data/v1/uploaded_file/delete/'
        logger.debug('upload file info payload: %s', data)
        logger.debug('upload file info url: %s', url)
        logger.debug('product id: %s', product_id)
        resp = yield treq.post(url, headers=header, json=data, persistent=False)
        confirm_info = yield treq.json_content(resp)
        logger.debug('upload file info to market confirm: %s', confirm_info)
        return confirm_info['status']

    @inlineCallbacks
    def add_follow_seller(self, seller_public_key=""):
        logger.debug("add seller following info to market")
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        logger.debug(self.public_key)
        data = {'public_key': self.public_key, 'seller_public_key': seller_public_key}
        url = self.url + 'product/v1/my_seller/subscribe/'
        logger.debug('upload file info payload: %s', data)
        logger.debug('upload file info url: %s', url)
        resp = yield treq.post(url, headers=header, json=data, persistent=False)
        confirm_info = yield treq.json_content(resp)
        logger.debug('upload file info to market confirm: %s', confirm_info)
        return confirm_info['status']

    @inlineCallbacks
    def add_follow_tag(self, tag="tag1"):
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        logger.debug(self.public_key)
        data = {'public_key': self.public_key, 'tag': tag}
        url = self.url + 'product/v1/my_tag/subscribe/'
        logger.debug('upload file info payload: %s', data)
        logger.debug('upload file info url: %s', url)
        resp = yield treq.post(url, headers=header, json=data, persistent=False)
        confirm_info = yield treq.json_content(resp)
        logger.debug('upload file info to market confirm: %s', confirm_info)
        return confirm_info['status']

    @inlineCallbacks
    def hide_product(self, market_hash=''):
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        logger.debug(self.public_key)
        data = {'market_hash': market_hash}
        url = self.url + 'product/v1/product/hide/'
        logger.debug('upload file info payload: %s', data)
        logger.debug('upload file info url: %s', url)
        resp = yield treq.post(url, headers=header, json=data, persistent=False)
        confirm_info = yield treq.json_content(resp)
        logger.debug('upload file info to market confirm: %s', confirm_info)
        return confirm_info['status']


    @inlineCallbacks
    def query_by_following_tag(self):
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        url = utils.build_url(self.url + "product/v1/my_tag/product/search/")
        logger.debug(url)
        resp = yield treq.get(url, headers=header)
        logger.debug(resp)
        comment_info = yield treq.json_content(resp)
        logger.debug('upload file info to market confirm: %s', comment_info)
        return comment_info['data']


    @inlineCallbacks
    def query_by_following_seller(self):
        header = {"MARKET-KEY": self.public_key, "MARKET-TOKEN": self.token,
                  'Content-Type': 'application/json'}
        url = utils.build_url(self.url + "product/v1/my_seller/product/search/")
        logger.debug(url)
        resp = yield treq.get(url, headers=header)
        logger.debug(resp)
        comment_info = yield treq.json_content(resp)
        logger.debug('query by following tag confirm: %s', comment_info)
        return comment_info['data']
