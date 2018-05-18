import unittest

from cpchain.market.market.utils import *
from tests.market.base_api_test import BaseApiTest


class UtilsTest(BaseApiTest):

    def test_load_key_pair_from_keystore(self):

        pri_key, pub_key = self.pri_key,self.pub_key

        # ---------- sign and verify ------------
        data = "testdata"
        new_signature = sign(pri_key, data)
        print("new_signature is:" + new_signature.hex())

        is_valid_sign = verify_signature(pub_key, new_signature, data)
        print("is valid new_signature:" + str(is_valid_sign))
        self.assertTrue(is_valid_sign, "should be success")

        is_valid_sign = verify_signature(pub_key, new_signature, data + "error")
        print("is valid new_signature:" + str(is_valid_sign))
        self.assertFalse(is_valid_sign, "should be failed")

    def test_get_address_from_public_key_object(self):

        pri_key, pub_key = self.pri_key, self.pub_key

        pub_key_string = ECCipher.serialize_public_key(pub_key)

        addr_hex_str = get_address_from_public_key_object(pub_key_string )
        print("addr_hex_str:%s" % addr_hex_str)
        self.assertIsNotNone(addr_hex_str)


if __name__ == '__main__':
    unittest.main()
