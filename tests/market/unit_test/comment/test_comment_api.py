from cpchain.market.transaction.models import TransactionDetail
from tests.market.base_api_test import *
from cpchain.market.market.utils import *

from tests.market.base_api_test_local import *
from rest_framework.test import APITestCase


class TestCommentApi(LocalBaseApiTest, APITestCase):

    def test_query_comment_list(self):

        token, market_hash = self.get_token_market_hash()
        self.add_comment_failed(token,market_hash)
        # self.add_comment_success(token, market_hash)

        params = {'market_hash':market_hash}
        url = reverse('comment_list')
        print("url:", url)
        resp_obj = self.client.get(url,params)
        print("resp_obj:%s" % resp_obj)
        resp_text = self.get_response_content(resp_obj)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        for p in parsed_json['data']:
            print("content:%s" % p["content"])

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

    def publish_product(self, token):
        title = "publish product 12444"
        description = "test12345654654654654"
        price = 9527
        tags = "tag1,tag2"
        start_date = "2018-04-01 10:10:10"
        end_date = "2018-12-10 10:10:10"
        file_md5 = "12345678901234567890"
        url = reverse('product_publish')
        payload = {'owner_address': self.pub_key_string, 'title': title, 'description': description, 'price': price,
                   'tags': tags, 'start_date': start_date, 'end_date': end_date, 'file_md5': file_md5}
        signature_source = self.pub_key_string + title + description + str(price) + start_date + end_date + file_md5

        new_signature = sign(self.pri_key, signature_source)
        print("new_signature is:" + new_signature.hex())

        payload['signature'] = new_signature.hex()
        print("publish product request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        publish_resp = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(publish_resp)

        self.assertEqual(publish_resp.status_code, 200)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)
        print("market_hash:%s" % parsed_json['data']["market_hash"])
        return parsed_json['data']["market_hash"]

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
        # response = requests.post(url, headers=header, json=payload)
        resp_obj = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(resp_obj)
        print("response:%s" % resp_obj)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)
