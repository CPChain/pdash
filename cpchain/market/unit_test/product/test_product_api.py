from rest_framework.test import APITestCase
from tests.market.base_api_test_local import *


class TestProductApi(LocalBaseApiTest, APITestCase):

    def test_query_recommend_products(self):
        token = self.login()
        self.publish_product(token)

        url = reverse('recommend_products')
        response = self.client.get(url)
        resp_text = self.get_response_content(response)
        print(resp_text)
        parsed_json = json.loads(resp_text)

        for p in parsed_json['data']:
            print("title:%s" % p["title"])
            print("sales_number:", p['sales_number'])

        self.assertGreaterEqual(1, len(parsed_json['data']))

    def test_query_you_may_like_product(self):
        token = self.login()
        self.publish_product(token)

        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}

        url = reverse('you_may_like_products')
        response = self.client.get(url, **header)
        resp_text = self.get_response_content(response)
        print(resp_text)
        parsed_json = json.loads(resp_text)

        for p in parsed_json['data']:
            print("title:%s" % p["title"])
            print("sales_number:", p['sales_number'])

        self.assertGreaterEqual(1, len(parsed_json['data']))

    def test_query_es_by_search(self):
        print('==========test_query_es_by_search===========')
        token = self.login()
        self.publish_product(token)
        self.query_es_product()

    def test_query_es_by_tag(self):
        token = self.login()
        self.publish_product(token)

        url = reverse('es_product_search')
        params = {"status": 0, "tag": 'tag1'}
        response = self.client.get(url, params)
        resp_text = self.get_response_content(response)
        parsed_json = json.loads(resp_text)

        result = parsed_json['results']
        for p in result:
            print("title:%s" % p["title"])

    def test_query_es_by_seller(self):
        token = self.login()
        self.publish_product(token)

        url = reverse('es_product_search')
        params = {"status": 0,
                  "seller": self.pub_key_string}
        response = self.client.get(url, params)
        resp_text = self.get_response_content(response)
        parsed_json = json.loads(resp_text)

        result = parsed_json['results']
        for p in result:
            print("title:%s" % p["title"])

    def test_query_es_by_market_hash(self):
        token = self.login()
        market_hash = self.publish_product(token)

        url = reverse('es_product_search')
        params = {"status": 0, "pid": market_hash}
        print('market_hash:', market_hash)
        response = self.client.get(url, params)
        resp_text = self.get_response_content(response)
        print("resp_text:%s" % resp_text)
        parsed_json = json.loads(resp_text)

        result = parsed_json['results']
        for p in result:
            print("title:%s" % p["title"])
            self.assertGreater(p['size'],1)

    def test_hide_or_show_es_product(self):
        token = self.login()
        self.publish_product(token)

        market_hash = self.publish_product(token)

        self.query_es_product()

        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}

        self.hide_product(header=header, market_hash=market_hash)

        self.query_es_product()

        self.show_product(header=header, market_hash=market_hash)

        self.query_es_product()

    def login_and_fetch_token(self):
        return self.login()

    def test_add_product_sales_quantity(self):
        token = self.login()
        self.publish_product(token)
        self.add_product_sales_quantity(token)

    def test_subscribe_tag_and_search_product(self):

        token = self.login()

        # # ======= publish product ========
        self.publish_product(token)

        # ======= subscribe tag ========
        self.subscribe_tag(token)

        # ======= query my tag ========
        self.query_my_tag(token)

        self.query_product_by_following_tag(token)

        # ======= unsubscribe tag ========
        self.unsubscribe_tag(token)

    def test_subscribe_seller_and_search_product(self):

        token = self.login()

        # ======= publish product ========
        self.publish_product(token)

        # ======= subscribe seller ========
        self.subscribe_seller(token)

        # ======= query by following seller ========
        self.query_my_seller(token)

        self.query_product_by_following_seller(token)

        # ======= unsubscribe seller ========
        self.unsubscribe_seller(token)

    def query_es_product(self):

        keyword = "publish"
        params = {"search": keyword, "status": 0}

        url = reverse('es_product_search')
        response = self.client.get(url, params)
        resp_text = self.get_response_content(response)
        print('query_es_product:', resp_text)
        parsed_json = json.loads(resp_text)

        result = parsed_json['results']
        for p in result:
            print("title:%s" % p["title"])

        self.assertGreaterEqual(len(result), 1)

    def add_product_sales_quantity(self, token):
        url = reverse('sales_quantity_add')
        payload = {'market_hash': 'market_hash_123'}
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        resp = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(resp)

        self.assertEqual(resp.status_code, 200)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)
        self.assertGreater(parsed_json['data'], 0)

    def subscribe_tag(self, token):

        url = reverse('product_tag_subscribe')
        payload = {'public_key': self.pub_key_string, 'tag': 'tag1'}
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        resp = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(resp)
        parsed_json = json.loads(resp_text)

        self.assertEqual(parsed_json['status'], 1)

    def unsubscribe_tag(self, token):
        url = reverse('product_tag_unsubscribe')
        payload = {'public_key': self.pub_key_string, 'tag': 'tag1'}
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        resp = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(resp)
        parsed_json = json.loads(resp_text)

        self.assertEqual(parsed_json['status'], 1)

    def query_product_by_following_tag(self, token):
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        url = reverse('my_tagged_product_search')
        response = self.client.get(url, format='json', **header)
        resp_text = self.get_response_content(response)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)

        for p in parsed_json['data']:
            print("title:%s" % p["title"])

    def subscribe_seller(self, token):
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        payload = {'public_key': self.pub_key_string, 'seller_public_key': self.pub_key_string}
        url = reverse('product_seller_subscribe')
        response = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(response)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)

        self.assertEqual(parsed_json['status'], 1)

    def unsubscribe_seller(self, token):
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        market_hash = self.publish_product(token)

        payload = {"seller_public_key": self.pub_key_string}
        url = reverse('product_seller_unsubscribe')
        response = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(response)
        print('unsubscribe seller:', resp_text)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)

        self.assertEqual(parsed_json['status'], 1)

    def query_my_seller(self, token):
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        url = reverse('product_my_seller_search')
        response = self.client.get(url, format='json', **header)
        resp_text = self.get_response_content(response)
        print('resp_text:', resp_text)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)

        self.assertGreaterEqual(len(parsed_json['data']), 1, "following seller's number should >=1")
        for p in parsed_json['data']:
            print("seller_public_key:%s" % p["seller_public_key"])

    def query_product_by_following_seller(self, token):
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        url = reverse('product_seller_search')
        response = self.client.get(url, format='json', **header)
        resp_text = self.get_response_content(response)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)

        self.assertGreaterEqual(len(parsed_json['data']), 1, "following seller's product number should >=1")
        for p in parsed_json['data']:
            print("title:%s" % p["title"])

    def query_my_tag(self, token):
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        url = reverse('my_tag_search')
        response = self.client.get(url, format='json', **header)
        resp_text = self.get_response_content(response)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)

        self.assertGreaterEqual(len(parsed_json['data']), 1, "my tag number should be >= 1")
        for p in parsed_json['data']:
            print("tag:%s" % p["tag"])

    def hide_product(self, header, market_hash):
        payload = {"market_hash": market_hash}
        url = reverse('product_hide')
        response = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(response)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)
        self.assertGreaterEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)
        return message

    def show_product(self, header, market_hash):
        payload = {"market_hash": market_hash}
        url = reverse('product_show')
        response = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(response)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)

        self.assertGreaterEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)
        return message
