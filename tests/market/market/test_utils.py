import unittest

from cpchain.market.market.utils import *
from cpchain.utils import Encoder
from tests.market.base_api_test import BaseApiTest


class UtilsTest(BaseApiTest):

    def test_load_key_pair_from_keystore(self):

        pri_key_string, pub_key_string = self.pri_key_string,self.pub_key_string
        print("pri_key_string:")
        print(pri_key_string)

        print("pub_key_string:")
        print(pub_key_string)

        # ---------- sign and verify ------------
        data = "testdata"
        new_signature = sign(pri_key_string, data)
        print("new_signature is:" + new_signature)

        is_valid_sign = verify_signature(pub_key_string, new_signature, data)
        print("is valid new_signature:" + str(is_valid_sign))
        self.assertTrue(is_valid_sign, "should be success")

        is_valid_sign = verify_signature(pub_key_string, new_signature, data + "error")
        print("is valid new_signature:" + str(is_valid_sign))
        self.assertFalse(is_valid_sign, "should be failed")

    def test_get_addr_from_public_key_object(self):

        pri_key_string, pub_key_string = self.pri_key_string, self.pub_key_string
        print("pri_key_string:")
        print(pri_key_string)

        print("pub_key_string:")
        print(pub_key_string)

        pub_key_bytes = Encoder.str_to_base64_byte(pub_key_string)

        addr_hex_str = get_addr_from_public_key_object(pub_key_bytes)
        print("addr_hex_str:%s" % addr_hex_str)
        self.assertIsNotNone(addr_hex_str)


if __name__ == '__main__':
    unittest.main()
