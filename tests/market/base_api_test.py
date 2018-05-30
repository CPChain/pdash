import json
import unittest

import requests
from cpchain.market.market.utils import *
from cpchain.crypto import ECCipher
from cpchain.utils import join_with_root, config, Encoder

HOST = "http://localhost:8083"
private_key_file1 = 'tests/market/assets/UTC--2018-01-25T08-04-38.217120006Z--22114f40ed222e83bbd88dc6cbb3b9a136299a23'
private_key_file2 = 'tests/market/assets/UTC--2018-04-12T02-42-29.929031000Z--7975bcf2faefec0dae6ccc82a66f89b12f23c747'
private_key_password_file = 'tests/market/assets/password'


class BaseApiTest(unittest.TestCase):

    def setUp(self):
        private_key_file_path1 = join_with_root(private_key_file1)
        private_key_file_path2 = join_with_root(private_key_file2)
        password_path = join_with_root(private_key_password_file)

        with open(password_path) as f:
            password = f.read()

        self.pri_key, self.pub_key = ECCipher.load_key_pair(private_key_file_path1, password)
        self.pri_key_2, self.pub_key_2 = ECCipher.load_key_pair(private_key_file_path2, password)

        self.pub_key_string = ECCipher.serialize_public_key(self.pub_key)
        self.pub_key_string2 = ECCipher.serialize_public_key(self.pub_key_2)

        self.address = ECCipher.get_address_from_public_key(self.pub_key)
        self.address_2 = ECCipher.get_address_from_public_key(self.pub_key_2)

    def _login_and_get_nonce(self, header):
        return self.__login_and_get_nonce(header, self.pub_key_string)

    def _generate_nonce_signature_and_get_token(self, header, nonce):
        return self.__generate_nonce_signature_and_get_token(header, nonce, self.pub_key_string, self.pri_key)

    def _login_and_get_nonce2(self, header):
        return self.__login_and_get_nonce(header,self.pub_key_string2)

    def _generate_nonce_signature_and_get_token2(self, header, nonce):
        return self.__generate_nonce_signature_and_get_token(header, nonce, self.pub_key_string2, self.pri_key_2)

    def __login_and_get_nonce(self, header, pub_key_str):
        payload = {"public_key": pub_key_str}
        url = '%s/account/v1/login/' % HOST
        response = requests.post(url, headers=header, json=payload)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(response.text)
        self.assertGreaterEqual(parsed_json['status'], 1)
        nonce = parsed_json['message']
        print("nonce:%s" % nonce)
        return nonce

    def __generate_nonce_signature_and_get_token(self, header, nonce, pub_key_str, pri_key):
        url = '%s/account/v1/confirm/' % HOST
        print("nonce:%s" % nonce)
        nonce_signature = ECCipher.create_signature(pri_key, nonce)

        payload = {"public_key": pub_key_str, "code": Encoder.bytes_to_hex(nonce_signature)}
        confirm_resp = requests.post(url, headers=header, json=payload)
        print("response:%s" , confirm_resp.text)
        self.assertEqual(confirm_resp.status_code, 200)
        parsed_json = json.loads(confirm_resp.text)
        self.assertEqual(parsed_json['status'], 1)
        token = parsed_json['message']
        print("token:%s" % token)
        return token


    def publish_product(self, token):
        title = "publish product 12444"
        description = "test12345654654654654"
        price = 9527
        tags = "tag1,tag2"
        start_date = "2018-04-01 10:10:10"
        end_date = "2018-12-10 10:10:10"
        file_md5 = "12345678901234567890"
        url = '%s/product/v1/product/publish/' % HOST
        payload = {'owner_address': self.pub_key_string, 'title': title,
                   'description': description, 'price': price, 'size': 10,
                   'tags': tags, 'start_date': start_date, 'end_date': end_date, 'file_md5': file_md5}
        signature_source = self.pub_key_string + title + description + str(price) + start_date + end_date + file_md5

        new_signature = sign(self.pri_key, signature_source)
        print("new_signature is:" + new_signature.hex())

        payload['signature'] = new_signature.hex()
        print("publish product request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        publish_resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(publish_resp.status_code, 200)
        print(publish_resp.text)
        parsed_json = json.loads(publish_resp.text)
        self.assertEqual(parsed_json['status'], 1)
        print("market_hash:%s" % parsed_json['data']["market_hash"])
        return parsed_json['data']["market_hash"]
