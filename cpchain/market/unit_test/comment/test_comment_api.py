from rest_framework.test import APITestCase
from cpchain.market.transaction.models import TransactionDetail
from tests.market.base_api_test_local import *


class TestCommentApi(LocalBaseApiTest, APITestCase):

    def test_query_comment_list(self):

        token, market_hash = self.get_token_market_hash()
        TransactionDetail.objects.create(seller_address=self.address_2, market_hash=market_hash,
                                         buyer_address=self.address)
        self.add_comment_success(token, market_hash)

        params = {'market_hash': market_hash}
        url = reverse('comment_list')
        print("url:", url)
        resp_obj = self.client.get(url,params)
        print("resp_obj:%s" % resp_obj)
        resp_text = self.get_response_content(resp_obj)
        print(resp_text)
        parsed_json = json.loads(resp_text)

        # {"data": [{
        #               "public_key": "045cfdf7cc44281ece607c85adbc2a2c17682e476a5b5f4ead5461a92aa078ffb46173d1949f4ea3e2d16658f6cf8eb92bab0f33811291bd79bdeca60d5a053a80",
        #               "market_hash": "RzZ3ZJ3WyK79T2zN3XE6sVbRMKLVuYm1bVroDhZiv+k=", "content": "test111", "rating": 1,
        #               "created": "2018-05-29T11:12:04.430689Z", "username": null, "avatar": null}], "status": 1,
        #  "message": "success"}
        for p in parsed_json['data']:
            print("public_key:%s" % p["public_key"])
            self.assertIsNotNone(p["public_key"])
            print("username:%s" % p["username"])
            print("avatar:%s" % p["avatar"])

    def test_add_comment_failed(self):

        token, market_hash = self.get_token_market_hash()
        self.add_comment_failed(token,market_hash)

    def test_add_comment_success(self):
        token, market_hash = self.get_token_market_hash()
        TransactionDetail.objects.create(seller_address=self.address_2, market_hash=market_hash,
                                         buyer_address=self.address)
        self.add_comment_success(token, market_hash)

    def test_query_summary_comment(self):
        token, market_hash = self.get_token_market_hash()
        url = reverse('get_summary_comment')
        params = {'market_hash': market_hash}
        summary_comment = self.client.get(url, params)
        print("summary_comment:%s" % summary_comment)
        resp_text = self.get_response_content(summary_comment)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)
        print("avg_rating:%s" % parsed_json['data']['avg_rating'])
        self.assertGreaterEqual(parsed_json['data']['avg_rating'],1)

    def get_token_market_hash(self):
        token = self.login()
        market_hash = self.publish_product(token)
        return token, market_hash

    def add_comment_failed(self, token, market_hash):
        url = reverse('comment_add')
        payload = {'public_key': self.pub_key_string, 'market_hash':market_hash, 'content':'test111'}
        print("add_comment request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}

        resp_obj = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(resp_obj)
        print("response:%s" % resp_obj)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 0)

    def add_comment_success(self, token, market_hash):
        # create tx record first
        url = reverse('comment_add')
        payload = {'public_key': self.pub_key_string, 'market_hash':market_hash, 'content':'test111'}
        print("add_comment request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}

        resp_obj = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(resp_obj)
        print("response:" % resp_obj)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)
