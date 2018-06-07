from tests.market.base_api_test import *
import os
import django
import urllib.parse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cpchain.market.market.settings")
django.setup()


from cpchain.market.transaction.models import TransactionDetail

class TestCommentApi(BaseApiTest):

    def test_query_comment_list(self):

        token, market_hash = self.get_token_market_hash()
        TransactionDetail.objects.create(seller_address=self.address_2, market_hash=market_hash,
                                         buyer_address=self.address)
        self.add_comment_success(token, market_hash)
        print("market_hash:", market_hash)

        url = '%s/comment/v1/comment/list/?market_hash=%s' % (HOST, urllib.parse.quote(market_hash))
        print("url:", url)
        response = requests.get(url)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        for p in parsed_json['data']:
            print("content:%s" % p["content"])

    def test_add_comment_failed(self):

        token, market_hash = self.get_token_market_hash()
        self.add_comment_failed(token,market_hash)

    def test_add_comment_success(self):
        token, market_hash = self.get_token_market_hash()
        # create TransactionDetail
        TransactionDetail.objects.create(seller_address=self.address_2, market_hash=market_hash,
                                         buyer_address=self.address)
        self.add_comment_success(token,market_hash)

    def test_query_summary_comment(self):
        token, market_hash = self.get_token_market_hash()

        url = '%s/comment/v1/summary_comment/?market_hash=%s' % (HOST, urllib.parse.quote(market_hash))
        summary_comment = requests.get(url)
        print("summary_comment:%s" % summary_comment)
        print(summary_comment.text)
        parsed_json = json.loads(summary_comment.text)
        self.assertEqual(parsed_json['status'], 1)
        print("avg_rating:%s" % parsed_json['data']['avg_rating'])
        self.assertGreaterEqual(parsed_json['data']['avg_rating'],1)

    def get_token_market_hash(self):
        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)

        # ======= generate nonce signature and confirm =======
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        market_hash = self.publish_product(token)
        return token,market_hash

    def add_comment_failed(self, token, market_hash):
        url = '%s/comment/v1/comment/add/' % HOST
        payload = {'market_hash':market_hash, 'content':'test111'}
        print("add_comment request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.post(url, headers=header, json=payload)

        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        self.assertEqual(parsed_json['status'], 0)

    def add_comment_success(self, token, market_hash):
        # TODO need create tx record first
        url = '%s/comment/v1/comment/add/' % HOST
        payload = {'public_key': self.pub_key_string, 'market_hash':market_hash, 'content':'test111'}
        print("add_comment request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.post(url, headers=header, json=payload)

        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        self.assertEqual(parsed_json['status'], 1)