from tests.market.base_api_test import *


class TestMainApi(BaseApiTest):

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
        url = '%s/main/v1/carousel/list/' % HOST
        response = requests.get(url)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

    def add_carousel(self):
        url = '%s/main/v1/carousel/add/' % HOST
        payload = {'name':'nnn','image':'cpchain/assets/wallet/icons/cpc-logo-single.png','link':'http://www.google.com'}
        header = {"MARKET-KEY": 'pub_key_string', "MARKET-TOKEN": 'token', 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(resp.status_code, 200)
        print(resp.text)
        parsed_json = json.loads(resp.text)
        self.assertEqual(parsed_json['status'], 1)
        print("message:%s" % parsed_json['message'])


    def query_hot_tag(self):
        url = '%s/main/v1/hot_tag/list/' % HOST
        response = requests.get(url)
        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

    def add_hot_tag(self):
        url = '%s/main/v1/hot_tag/add/' % HOST
        payload = {'tag':'t1','image':'cpchain/assets/wallet/icons/cpc-logo-single.png'}
        header = {"MARKET-KEY": 'pub_key_string', "MARKET-TOKEN": 'token', 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(resp.status_code, 200)
        print(resp.text)
        parsed_json = json.loads(resp.text)
        self.assertEqual(parsed_json['status'], 1)
        print("message:%s" % parsed_json['message'])


    def query_promotion(self):
        url = '%s/main/v1/promotion/list/' % HOST
        response = requests.get(url)
        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

    def add_promotion(self):
        url = '%s/main/v1/promotion/add/' % HOST
        payload = {'link':'http://111.222.com','image':'cpchain/assets/wallet/icons/cpc-logo-single.png'}
        header = {"MARKET-KEY": 'pub_key_string', "MARKET-TOKEN": 'token', 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(resp.status_code, 200)
        print(resp.text)
        parsed_json = json.loads(resp.text)
        self.assertEqual(parsed_json['status'], 1)
        print("message:%s" % parsed_json['message'])