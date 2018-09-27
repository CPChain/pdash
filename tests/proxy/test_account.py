import unittest
import json

from cpchain.account import Account
from cpchain.proxy import account

encrypted_key = {"address": "757a2b31af15fd539f3a461a15d5b95ad33b4eee", "id": "30d6b02e-d39c-4d9e-a580-8752850a8324", "version": 3, "crypto": {"kdf": "pbkdf2", "cipherparams": {"iv": "d2418cff6a0f23871fe21b288fe5fe18"}, "kdfparams": {"dklen": 32, "prf": "hmac-sha256", "salt": "34281e437ca600e159d8f7533ffc0e3f", "c": 1000000}, "mac": "ce0eaa5e65b57a2c224ff71437b55d3ca7c739a646723a7e09c916bb3990e319", "ciphertext": "b47aed1b93acaa270d14f3dce9084cb073e67dbe687340f75845817d4668e6fe", "cipher": "aes-128-ctr"}}

keystore = '/tmp/keystore'

with open(keystore, 'w') as f:
    f.write(json.dumps(encrypted_key))

account._proxy_account = Account(keystore, b'passwd')

from cpchain.proxy.account import get_proxy_id, sign_proxy_data, derive_proxy_data


class AccountTest(unittest.TestCase):
    def test_account(self):
        proxy_id = get_proxy_id()
        self.assertIsNotNone(proxy_id)
        test_data = 'test string'
        sign_data = sign_proxy_data(test_data)
        data = derive_proxy_data(sign_data)
        self.assertEqual(data, test_data)
