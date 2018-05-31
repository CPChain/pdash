from rest_framework.test import APITestCase

from tests.market.base_api_test_local import *


class TestMainApi(LocalBaseApiTest, APITestCase):

    def test_carousel(self):
        self.add_carousel()
        self.query_carousel()

    def test_hot_tag(self):
        self.add_hot_tag()
        self.query_hot_tag()

    def test_promotion(self):
        self.add_promotion()
        self.query_promotion()

    def query_carousel(self):
        url = reverse('carousel_list')

        response = self.client.get(url)
        resp_text = self.get_response_content(response)

        print("products:%s" % response)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)
        print("message:%s" % parsed_json['message'])

    def add_carousel(self):
        url = reverse('carousel_add')
        payload = {'name':'nnn','image':'cpchain/assets/wallet/icons/cpc-logo-single.png','link':'http://www.google.com'}
        header = {"MARKET-KEY": 'pub_key_string', "MARKET-TOKEN": 'token', 'Content-Type': 'application/json'}

        resp = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(resp)
        self.assertEqual(resp.status_code, 200)

        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)
        print("message:%s" % parsed_json['message'])

    def query_hot_tag(self):
        url = reverse('hot_tag_list')
        response = self.client.get(url)
        resp_text = self.get_response_content(response)

        print("response:%s" % response)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)
        print("message:%s" % parsed_json['message'])

    def add_hot_tag(self):
        payload = {'tag':'t1','image':'cpchain/assets/wallet/icons/cpc-logo-single.png'}
        header = {"MARKET-KEY": 'pub_key_string', "MARKET-TOKEN": 'token', 'Content-Type': 'application/json'}
        url = reverse('hot_tag_add')
        resp = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(resp)

        self.assertEqual(resp.status_code, 200)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)
        print("message:%s" % parsed_json['message'])

    def query_promotion(self):
        url = reverse('promotion_list')

        response = self.client.get(url)
        resp_text = self.get_response_content(response)

        print("response:%s" % response)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)
        print("message:%s" % parsed_json['message'])

    def add_promotion(self):
        url = reverse('promotion_add')
        payload = {'link':'http://111.222.com','image':'cpchain/assets/wallet/icons/cpc-logo-single.png'}
        header = {"MARKET-KEY": 'pub_key_string', "MARKET-TOKEN": 'token', 'Content-Type': 'application/json'}
        resp = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(resp)

        self.assertEqual(resp.status_code, 200)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)
        print("message:%s" % parsed_json['message'])
