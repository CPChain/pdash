import json
import unittest

import requests

from cpchain.crypto import ECCipher
from cpchain.utils import join_with_root, config

HOST = "http://localhost:8083"
private_key_file = 'tests/market/assets/UTC--2018-01-25T08-04-38.217120006Z--22114f40ed222e83bbd88dc6cbb3b9a136299a23'
private_key_password_file = 'tests/market/assets/password'


def generate_nonce_signature(priv_key, nonce):
    print("priv_key:%s, nonce:%s" % (priv_key ,nonce))
    signature = ECCipher.generate_string_signature(priv_key, nonce)
    return signature


class BaseApiTest(unittest.TestCase):

    def setUp(self):
        private_key_file_path = join_with_root(private_key_file)
        password_path = join_with_root(private_key_password_file)

        with open(password_path) as f:
            password = f.read()

        self.pri_key_string, self.pub_key_string = ECCipher.load_key_pair_from_keystore(private_key_file_path, password)
