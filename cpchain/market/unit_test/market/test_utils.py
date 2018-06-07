import unittest

from cpchain.market.market.utils import *
from tests.market.base_api_test import BaseApiTest
from django.utils.http import quote,unquote

class UtilsTest(BaseApiTest):

    def test_url_encode(self):
        pp = "QwToU/09ys0B8SVKmBnv5OKTax2s1+Mlxj0OywiF77U="
        encoded = quote(pp)
        print("\n")
        print(encoded)
        self.assertEquals("QwToU/09ys0B8SVKmBnv5OKTax2s1%2BMlxj0OywiF77U%3D",encoded)

        decoded = unquote(encoded)
        print(decoded)
        self.assertEquals(pp, decoded)

        decoded = unquote(encoded)
        print(decoded)
        self.assertEquals(pp, decoded)



    def test_gen_sign(self):
        title = "publish product 12444"
        description = "test12345654654654654"
        price = 9527
        start_date = "2018-04-01 10:10:10"
        end_date = "2018-12-10 10:10:10"
        file_md5 = "12345678901234567890"
        signature_source = self.pub_key_string + title + description + str(price) + start_date + end_date + file_md5

        new_signature = sign(self.pri_key, signature_source)
        print("new_signature is:" + new_signature.hex())
        self.assertIsNotNone(new_signature)

    def test_load_key_pair_from_keystore(self):
        pri_key, pub_key = self.pri_key, self.pub_key

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

        addr_hex_str = get_address_from_public_key_object(pub_key_string)
        print("addr_hex_str:%s" % addr_hex_str)
        self.assertIsNotNone(addr_hex_str)

    def test_short_name_success(self):
        name = get_short_name('HTTP_MARKET_KEY')
        self.assertEquals('MARKET-KEY', name)

    def test_short_name_original(self):
        name = get_short_name('MARKET-KEY')
        self.assertEquals('MARKET-KEY', name)


if __name__ == '__main__':
    unittest.main()
