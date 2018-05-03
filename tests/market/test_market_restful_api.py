# Create your tests here.

import json
import unittest

import requests

from cpchain.crypto import ECCipher
from cpchain.utils import join_with_root, config

HOST = "http://localhost:8083"


def generate_nonce_signature(priv_key, nonce):
    print("priv_key:%s, nonce:%s" % (priv_key ,nonce))
    signature = ECCipher.geth_sign(priv_key, nonce)
    return signature


class TestMarketApi(unittest.TestCase):

    def setUp(self):
        private_key_file_path = join_with_root(config.wallet.private_key_file)
        password_path = join_with_root(config.wallet.private_key_password_file)

        with open(password_path) as f:
            password = f.read()

        self.pri_key_string, self.pub_key_string = ECCipher.geth_load_key_pair_from_private_key(private_key_file_path, password)

        # print("pub_key:%s,pri_key:%s,password:%s" % (self.pub_key_string, self.pri_key_string , password))

    def test_query_from_db(self):
        keyword = "z7JI8DccklHodvexTCDmLxdviNtKhhRJU8bvv4vKoTc="
        self.query_product(keyword=keyword)

        keyword = "testtile"
        self.query_product(keyword=keyword)

    def test_login_and_confirm(self):

        header = {'Content-Type': 'application/json'}
        nonce = self.login_and_get_nonce(header)

        # ======= generate nonce signature and confirm =======
        token = self.generate_nonce_signature_and_get_token(header, nonce)

        # ======= publish product ========
        self.publish_product(token)

        # ======= query product ========
        keyword = "testtile"
        self.query_product(keyword=keyword)

        # ======= query product via elasticsearch ========
        self.query_es_product()

    def login_and_get_nonce(self, header):
        payload = {"public_key": self.pub_key_string}
        url = '%s/api/v1/login/' % HOST
        response = requests.post(url, headers=header, json=payload)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(response.text)
        # print(response.text)
        self.assertEqual(parsed_json['success'], True)
        nonce = parsed_json['message']
        return nonce

    def generate_nonce_signature_and_get_token(self, header, nonce):
        url = '%s/api/v1/confirm/' % HOST
        nonce_signature = generate_nonce_signature(self.pri_key_string, nonce)
        payload = {"public_key": self.pub_key_string, "code": nonce_signature}
        # print("confirm request:%s" % payload)
        confirm_resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(confirm_resp.status_code, 200)
        parsed_json = json.loads(confirm_resp.text)
        self.assertEqual(parsed_json['success'], True)
        token = parsed_json['message']
        print("token:%s" % token)
        return token

    def query_product(self, keyword):
        params = {"keyword": keyword}
        url = '%s/api/v1/product/search/' % HOST
        response = requests.get(url, params)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        for p in parsed_json:
            print("title:%s" % p["title"])

    def query_es_product(self):
        keyword = "testtile"
        params = {"keyword": keyword}
        url = '%s/api/v1/es_product/search/' % HOST
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
        url = '%s/api/v1/product/publish/' % HOST
        payload = {'owner_address': self.pub_key_string, 'title': title, 'description': description, 'price': price,
                   'tags': tags, 'start_date': start_date, 'end_date': end_date, 'file_md5': file_md5}
        signature_source = self.pub_key_string + title + description + str(price) + start_date + end_date + file_md5
        signature = ECCipher.geth_sign(self.pri_key_string, signature_source)
        payload['signature'] = signature
        print("publish product request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        publish_resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(publish_resp.status_code, 200)
        print(publish_resp.text)
        parsed_json = json.loads(publish_resp.text)
        self.assertEqual(parsed_json['status'], 1)
        print("market_hash:%s" % parsed_json['data']["market_hash"])



