import json
import unittest

import requests

from cpchain.crypto import ECCipher
from cpchain.utils import join_with_root, config

HOST = "http://localhost:8083"
private_key_file1 = 'tests/market/assets/UTC--2018-01-25T08-04-38.217120006Z--22114f40ed222e83bbd88dc6cbb3b9a136299a23'
private_key_file2 = 'tests/market/assets/UTC--2018-04-12T02-42-29.929031000Z--7975bcf2faefec0dae6ccc82a66f89b12f23c747'
private_key_password_file = 'tests/market/assets/password'


def generate_nonce_signature(priv_key, nonce):
    print("priv_key:%s, nonce:%s" % (priv_key ,nonce))
    signature = ECCipher.generate_string_signature(priv_key, nonce)
    return signature


class BaseApiTest(unittest.TestCase):

    def setUp(self):
        private_key_file_path1 = join_with_root(private_key_file1)
        private_key_file_path2 = join_with_root(private_key_file2)
        password_path = join_with_root(private_key_password_file)

        with open(password_path) as f:
            password = f.read()

        self.pri_key_string, self.pub_key_string = ECCipher.load_key_pair_from_keystore(private_key_file_path1, password)
        self.pri_key_string2, self.pub_key_string2 = ECCipher.load_key_pair_from_keystore(private_key_file_path2, password)

    def _login_and_get_nonce(self, header):
        # payload = {"public_key": self.pub_key_string}
        # url = '%s/account/v1/login/' % HOST
        # response = requests.post(url, headers=header, json=payload)
        # self.assertEqual(response.status_code, 200)
        # parsed_json = json.loads(response.text)
        # # print(response.text)
        # self.assertGreaterEqual(parsed_json['status'], 1)
        # nonce = parsed_json['message']
        # print("nonce:%s" % nonce)
        # return nonce
        return self.__login_and_get_nonce(header, self.pub_key_string)

    def _generate_nonce_signature_and_get_token(self, header, nonce):
        return self.__generate_nonce_signature_and_get_token(header, nonce, self.pub_key_string, self.pri_key_string)

    def _login_and_get_nonce2(self, header):
        return self.__login_and_get_nonce(header,self.pub_key_string2)

    def _generate_nonce_signature_and_get_token2(self, header, nonce):
        return self.__generate_nonce_signature_and_get_token(header, nonce, self.pub_key_string2, self.pri_key_string2)

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

    def __generate_nonce_signature_and_get_token(self, header, nonce, pub_key_str, pri_key_str):
        url = '%s/account/v1/confirm/' % HOST
        nonce_signature = generate_nonce_signature(pri_key_str, nonce)
        payload = {"public_key": pub_key_str, "code": nonce_signature}
        confirm_resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(confirm_resp.status_code, 200)
        parsed_json = json.loads(confirm_resp.text)
        self.assertEqual(parsed_json['status'], 1)
        token = parsed_json['message']
        print("token:%s" % token)
        return token
