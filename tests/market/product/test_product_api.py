from django.utils.http import urlquote
from tests.market.base_api_test import *


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

    def test_query_from_db(self):
        keyword = "z7JI8DccklHodvexTCDmLxdviNtKhhRJU8bvv4vKoTc="
        self.query_product(keyword=keyword)

        keyword = "testtile"
        self.query_product(keyword=keyword)

    def test_query_es_product(self):

        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)

        token = self._generate_nonce_signature_and_get_token(header, nonce)

        self.publish_product(token)

        # ======= query product ========
        keyword = "testtile"
        self.query_product(keyword=keyword)

        # ======= query product via elasticsearch ========
        self.query_es_product()

    def test_add_product_sales_quantity(self):

        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)

        token = self._generate_nonce_signature_and_get_token(header, nonce)

        self.add_product_sales_quantity(token)

    def test_subscribe_tag_and_search_product(self):

        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)

        # ======= generate nonce signature and confirm =======
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        # # ======= publish product ========
        self.publish_product(token)

        # ======= subscribe tag ========
        self.subscribe_tag(token)

        # ======= query my tag ========
        self.query_my_tag(token)

        # ======= unsubscribe tag ========
        self.unsubscribe_tag(token)

    def test_subscribe_seller_and_search_product(self):

        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)

        # ======= generate nonce signature and confirm =======
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        # ======= publish product ========
        self.publish_product(token)

        # ======= subscribe seller ========
        self.subscribe_seller(token)

        # ======= query by following seller ========
        self.query_my_seller(token)

        # ======= unsubscribe seller ========
        self.unsubscribe_seller(token)

    def query_product(self, keyword):
        params = {"keyword": keyword}
        url = '%s/product/v1/product/search/' % HOST
        response = requests.get(url, params)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        for p in parsed_json:
            print("title:%s" % p["title"])

    def query_es_product(self):
        keyword = "testtile"
        params = {"keyword": keyword}
        url = '%s/product/v1/es_product/search/' % HOST
        response = requests.get(url, params)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

        result = parsed_json['results']
        for p in result:
            print("title:%s" % p["title"])

    def publish_product(self, token):
        title = "publish product 12444"
        description = "test12345654654654654"
        price = 9527
        tags = "tag1,tag2"
        start_date = "2018-04-01 10:10:10"
        end_date = "2018-12-10 10:10:10"
        file_md5 = "12345678901234567890"
        url = '%s/product/v1/product/publish/' % HOST
        payload = {'owner_address': self.pub_key_string, 'title': title, 'description': description, 'price': price,
                   'tags': tags, 'start_date': start_date, 'end_date': end_date, 'file_md5': file_md5}
        signature_source = self.pub_key_string + title + description + str(price) + start_date + end_date + file_md5
        signature = ECCipher.generate_string_signature(self.pri_key_string, signature_source)
        payload['signature'] = signature
        print("publish product request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        publish_resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(publish_resp.status_code, 200)
        print(publish_resp.text)
        parsed_json = json.loads(publish_resp.text)
        self.assertEqual(parsed_json['status'], 1)
        print("market_hash:%s" % parsed_json['data']["market_hash"])

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

    def query_subscribed_tag(self, token):
        url = '%s/product/v1/my_tag/search/' % HOST
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.get(url, headers=header)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        for p in parsed_json['data']:
            print("title:%s" % p["title"])

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

    def test_query_product_by_seller(self):
        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        self.publish_product(token)

        url = '%s/product/v1/search_by_seller/?seller=%s' % (HOST, urlquote(self.pub_key_string))
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.get(url, headers=header)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        self.assertGreaterEqual(len(parsed_json['data']), 1, "product number should be >= 1")
        for p in parsed_json['data']:
            print("tags:%s" % p["tags"])

    def test_query_product_by_tag(self):
        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        self.publish_product(token)

        url = '%s/product/v1/search_by_tag/?tag=%s' % (HOST, 'tag1')
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.get(url, headers=header)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        self.assertGreaterEqual(len(parsed_json['data']), 1, "product number should be >= 1")
        for p in parsed_json['data']:
            print("tags:%s" % p["tags"])