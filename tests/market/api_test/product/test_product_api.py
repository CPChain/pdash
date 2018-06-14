from django.utils.http import urlquote
from tests.market.base_api_test import *
from cpchain.market.market.utils import *


class TestProductApi(BaseApiTest):

    def test_query_recommend_products(self):
        url = '%s/product/v1/recommend_product/list/' % HOST
        response = requests.get(url)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        for p in parsed_json['data']:
            print("title:%s" % p["title"])
            print("sales_number:", p['sales_number'])

    def test_query_you_may_like_product(self):
        token = self.login_and_fetch_token()
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        url = '%s/product/v1/you_may_like/list/' % HOST
        response = requests.get(url, headers=header)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        for p in parsed_json['data']:
            print("title:%s" % p["title"])
            print("sales_number:", p['sales_number'])

    # # TODO remove me
    # def test_query_from_db(self):
    #     keyword = "z7JI8DccklHodvexTCDmLxdviNtKhhRJU8bvv4vKoTc="
    #     self.query_product(keyword=keyword)
    #
    #     keyword = "testtile"
    #     self.query_product(keyword=keyword)

    # # TODO remove me
    # def test_query_paged_product(self):
    #     keyword = "publish"
    #     self.query_paged_product(keyword=keyword)

    def test_query_es_by_search(self):

        token = self.login_and_fetch_token()

        self.publish_product(token)

        # ======= query product via elasticsearch ========
        self.query_es_product()

    def test_query_es_by_tag(self):
        url = '%s/product/v1/es_product/search/?status=0&tag=tag1' % HOST
        response = requests.get(url)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

        result = parsed_json['results']
        for p in result:
            print("title:%s" % p["title"])
            self.assertGreater(p['size'], 1)

    def test_query_es_by_seller_with_limit(self):
        url = '%s/product/v1/es_product/search/?ordering=-created&offset=0&limit=2&status=0&seller=045cfdf7cc44281ece607c85adbc2a2c17682e476a5b5f4ead5461a92aa078ffb46173d1949f4ea3e2d16658f6cf8eb92bab0f33811291bd79bdeca60d5a053a80' % HOST
        response = requests.get(url)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

        result = parsed_json['results']
        for p in result:
            print("title:%s,created:%s" % (p["title"], p["created"]))
            self.assertGreater(p['size'], 1)

    def test_query_es_by_seller(self):
        url = '%s/product/v1/es_product/search/?status=0&seller=045cfdf7cc44281ece607c85adbc2a2c17682e476a5b5f4ead5461a92aa078ffb46173d1949f4ea3e2d16658f6cf8eb92bab0f33811291bd79bdeca60d5a053a80' % HOST
        response = requests.get(url)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

        result = parsed_json['results']
        for p in result:
            print("title:%s" % p["title"])
            self.assertGreater(p['size'], 1)

    def test_query_es_by_market_hash(self):
        url = '%s/product/v1/es_product/search/?status=0&pid=1xrqb9w9AUQguQE4Cds1q3VQQPojVUPNfwE2G19qVNo=' % HOST
        response = requests.get(url)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

        result = parsed_json['results']
        for p in result:
            print("title:%s" % p["title"])
            self.assertGreater(p['size'], 1)

    def test_hide_or_show_es_product(self):

        token = self.login_and_fetch_token()

        market_hash = self.publish_product(token)

        # ======= query product via elasticsearch ========
        self.query_es_product()

        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}

        self.hide_product(header=header,market_hash=market_hash)

        self.query_es_product()

        self.show_product(header=header,market_hash=market_hash)

        self.query_es_product()




    def login_and_fetch_token(self):
        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)
        token = self._generate_nonce_signature_and_get_token(header, nonce)
        return token

    def test_add_product_sales_quantity(self):

        token = self.login_and_fetch_token()

        self.add_product_sales_quantity(token)

    def test_subscribe_tag_and_search_product(self):

        token = self.login_and_fetch_token()

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

        token = self.login_and_fetch_token()

        # ======= publish product ========
        self.publish_product(token)

        # ======= subscribe seller ========
        self.subscribe_seller(token)

        # ======= query by following seller ========
        self.query_my_seller(token)

        # ======= unsubscribe seller ========
        self.unsubscribe_seller(token)

    def query_es_product(self):
        keyword = "Medicine"
        params = {"search": keyword,"status":0}
        url = '%s/product/v1/es_product/search/' % HOST
        response = requests.get(url, params)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

        result = parsed_json['results']
        for p in result:
            print("title:%s" % p["title"])
            self.assertGreater(p['size'], 1)

    def add_product_sales_quantity(self, token):
        url = '%s/product/v1/sales_quantity/add/' % HOST
        payload = {'market_hash': 'market_hash_123'}
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(resp.status_code, 200)
        print(resp.text)
        parsed_json = json.loads(resp.text)
        self.assertEqual(parsed_json['status'], 1)
        self.assertGreater(parsed_json['data'], 0)

    def subscribe_tag(self, token):
        url = '%s/product/v1/my_tag/subscribe/' % HOST
        payload = {'public_key': self.pub_key_string, 'tag': 'tag1'}
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(resp.status_code, 200)
        print(resp.text)
        parsed_json = json.loads(resp.text)
        self.assertEqual(parsed_json['status'], 1)

    def unsubscribe_tag(self, token):
        url = '%s/product/v1/my_tag/unsubscribe/' % HOST
        payload = {'public_key': self.pub_key_string, 'tag': 'tag1'}
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(resp.status_code, 200)
        print(resp.text)
        parsed_json = json.loads(resp.text)
        self.assertEqual(parsed_json['status'], 1)

    def query_product_by_following_tag(self, token):
        url = '%s/product/v1/my_tag/product/search/' % HOST
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.get(url, headers=header)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        for p in parsed_json['data']:
            print("title:%s" % p["title"])

    def subscribe_seller(self, token):
        url = '%s/product/v1/my_seller/subscribe/' % HOST
        payload = {'public_key': self.pub_key_string,'seller_public_key': self.pub_key_string}
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(resp.status_code, 200)
        print(resp.text)
        parsed_json = json.loads(resp.text)
        self.assertEqual(parsed_json['status'], 1)

    def unsubscribe_seller(self, token):
        url = '%s/product/v1/my_seller/unsubscribe/' % HOST
        payload = {'public_key': self.pub_key_string,'seller_public_key': 'sss1'}
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(resp.status_code, 200)
        print(resp.text)
        parsed_json = json.loads(resp.text)
        self.assertEqual(parsed_json['status'], 1)

    def query_my_seller(self, token):
        url = '%s/product/v1/my_seller/search/' % HOST
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.get(url,headers=header)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        self.assertGreaterEqual(len(parsed_json['data']), 1, "following seller's number should >=1")
        for p in parsed_json['data']:
            print("seller_public_key:%s" % p["seller_public_key"])

    def query_product_by_following_seller(self, token):
        url = '%s/product/v1/my_seller_product/search/' % HOST
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.get(url, headers=header)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        self.assertGreaterEqual(len(parsed_json['data']), 1, "following seller's product number should >=1")
        for p in parsed_json['data']:
            print("title:%s" % p["title"])

    def query_my_tag(self, token):
        url = '%s/product/v1/my_tag/search/' % HOST
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.get(url, headers=header)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        self.assertGreaterEqual(len(parsed_json['data']), 1 ,"my tag number should be >= 1")
        for p in parsed_json['data']:
            print("tag:%s" % p["tag"])

    # def test_query_product_by_seller(self):
    #     token = self.login_and_fetch_token()
    #
    #     self.publish_product(token)
    #
    #     url = '%s/product/v1/search_by_seller/?seller=%s' % (HOST, urlquote(self.pub_key_string))
    #     header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
    #     response = requests.get(url, headers=header)
    #     print("products:%s" % response)
    #     print(response.text)
    #     parsed_json = json.loads(response.text)
    #     self.assertGreaterEqual(len(parsed_json['data']), 1, "product number should be >= 1")
    #     for p in parsed_json['data']:
    #         print("tags:%s" % p["tags"])
    #
    # def test_query_product_by_tag(self):
    #     token = self.login_and_fetch_token()
    #
    #     self.publish_product(token)
    #
    #     url = '%s/product/v1/search_by_tag/?tag=%s' % (HOST, 'tag1')
    #     header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
    #     response = requests.get(url, headers=header)
    #     print("products:%s" % response)
    #     print(response.text)
    #     parsed_json = json.loads(response.text)
    #     self.assertGreaterEqual(len(parsed_json['data']), 1, "product number should be >= 1")
    #     for p in parsed_json['data']:
    #         print("tags:%s" % p["tags"])

    def hide_product(self, header, market_hash):
        payload = {"market_hash": market_hash}
        url = '%s/product/v1/product/hide/' % HOST
        response = requests.post(url, headers=header, json=payload)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(response.text)
        self.assertGreaterEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)
        return message

    def show_product(self, header, market_hash):
        payload = {"market_hash": market_hash}
        url = '%s/product/v1/product/show/' % HOST
        response = requests.post(url, headers=header, json=payload)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(response.text)
        self.assertGreaterEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)
        return message