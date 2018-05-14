from tests.market.base_api_test import *


class TestAccountAndProductApi(BaseApiTest):

    def setUp(self):
        private_key_file_path = join_with_root(private_key_file)
        password_path = join_with_root(private_key_password_file)

        with open(password_path) as f:
            password = f.read()

        self.pri_key_string, self.pub_key_string = ECCipher.load_key_pair_from_keystore(private_key_file_path, password)

        # print("pub_key:%s,pri_key:%s,password:%s" % (self.pub_key_string, self.pri_key_string , password))

    def test_query_recommend_products(self):
        self.query_recommend_products()


    def test_query_from_db(self):
        keyword = "z7JI8DccklHodvexTCDmLxdviNtKhhRJU8bvv4vKoTc="
        self.query_product(keyword=keyword)

        keyword = "testtile"
        self.query_product(keyword=keyword)

    def test_login_and_confirm(self):

        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)

        # ======= generate nonce signature and confirm =======
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        # ======= publish product ========
        self.publish_product(token)

        # ======= query product ========
        keyword = "testtile"
        self.query_product(keyword=keyword)

        # ======= query product via elasticsearch ========
        self.query_es_product()

    def test_add_product_sales_quantity(self):

        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_noncelogin_and_get_nonce(header)

        # ======= generate nonce signature and confirm =======
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        # ======= publish product ========
        self.publish_product(token)

        # ======= TODO add product_sales_quantity ========
        self.add_product_sales_quantity(token)

    def test_subscribe_tag(self):

        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_noncelogin_and_get_nonce(header)

        # ======= generate nonce signature and confirm =======
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        # ======= publish product ========
        self.publish_product(token)

        # ======= TODO subscribe tag ========
        self.subscribe_tag(token)

        # ======= TODO unsubscribe tag ========
        self.unsubscribe_tag(token)

        # ======= TODO query by following tag =======
        self.query_by_subscribe_tag(token)

    def test_subscribe_seller(self):

        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_noncelogin_and_get_nonce(header)

        # ======= generate nonce signature and confirm =======
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        # ======= publish product ========
        self.publish_product(token)

        # ======= TODO subscribe seller ========
        self.subscribe_seller(token)

        # ======= TODO unsubscribe seller ========
        self.unsubscribe_seller(token)

        # ======= TODO query by following seller ========
        self.query_by_subscribe_seller(token)

    def query_recommend_products(self):
        # TODO
        url = '%s/product/v1/recommend_product/list/' % HOST
        response = requests.get(url)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        for p in parsed_json['data']:
            print("title:%s" % p["title"])

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
        url = '%s/product/v1/product/sales_quantity/add/' % HOST
        payload = {'market_hash': 'market_hash_123'}
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(resp.status_code, 200)
        print(resp.text)
        parsed_json = json.loads(resp.text)
        self.assertEqual(parsed_json['status'], 1)
        self.assertGreater(parsed_json['data']['quantity'], 0)

    def subscribe_tag(self, token):
        url = '%s/product/v1/product/tag/subscribe/' % HOST
        payload = {'public_key': self.pub_key_string, 'tag': 'tag1'}
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(resp.status_code, 200)
        print(resp.text)
        parsed_json = json.loads(resp.text)
        self.assertEqual(parsed_json['status'], 1)

    def unsubscribe_tag(self, token):
        url = '%s/product/v1/product/tag/unsubscribe' % HOST
        payload = {'public_key': self.pub_key_string, 'tag': 'tag1'}
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(resp.status_code, 200)
        print(resp.text)
        parsed_json = json.loads(resp.text)
        self.assertEqual(parsed_json['status'], 1)

    def subscribe_seller(self, token):
        url = '%s/product/v1/product/seller/subscribe/' % HOST
        payload = {'public_key': self.pub_key_string,'seller_public_key': 'sss1'}
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(resp.status_code, 200)
        print(resp.text)
        parsed_json = json.loads(resp.text)
        self.assertEqual(parsed_json['status'], 1)

    def unsubscribe_seller(self, token):
        url = '%s/product/v1/product/seller/unsubscribe/' % HOST
        payload = {'public_key': self.pub_key_string,'seller_public_key': 'sss1'}
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(resp.status_code, 200)
        print(resp.text)
        parsed_json = json.loads(resp.text)
        self.assertEqual(parsed_json['status'], 1)

    def query_by_subscribe_seller(self, token):
        url = '%s/product/v1/product/seller/search/' % HOST
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.get(url,headers=header)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        for p in parsed_json['data']:
            print("title:%s" % p["title"])

    def query_by_subscribe_tag(self, token):
        url = '%s/product/v1/product/tag/search/' % HOST
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.get(url, headers=header)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        for p in parsed_json['data']:
            print("title:%s" % p["title"])


