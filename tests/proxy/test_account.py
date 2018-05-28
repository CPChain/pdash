import unittest

from cpchain.proxy.account import set_proxy_account, get_proxy_id, \
                                sign_proxy_data, derive_proxy_data

class AccountTest(unittest.TestCase):
    def test_account(self):
        set_proxy_account()
        proxy_id = get_proxy_id()
        self.assertIsNotNone(proxy_id)
        test_data = 'test string'
        sign_data = sign_proxy_data(test_data)
        data = derive_proxy_data(sign_data)
        self.assertEqual(data, test_data)
