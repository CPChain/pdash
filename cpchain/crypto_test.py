import unittest

from cpchain.utils import join_with_root,config
from cpchain.crypto import ECCipher

private_key_string = "MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAixihD8Ld8YbQICCAAwDAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEG44GNJc06XGWEgbpaGvhB4EgZC/fiBy6TUHehjKFtDI7CE7X26c6yHcLjjDaNDCVYTnSKf12WdzwBbpwbKfM3yOpDessx2Ny6l9UtnDX5rjQjfgNzI61xa+j1SXGIAjd8atlnqULfPnzn2N9TfS9pEY7S6NGrYvhkzbZrejdtM+pl5F/0IJGszP6VSWSZrt+k7NNakfw6uz9VqnBhkIWk+hKJQ="
public_key_string = "MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAE8s5X7ql5VAr6nfGkkvT5t4uMtSKBivQL6rtwmBZ0C+E2WHR8EqU9X+gElHAaY4b0OUyEqZ17omkqvzaDsNo24g=="


class CryptosTest(unittest.TestCase):

    def test_generate_key_pair_signature_and_verify(self):
        sample = b"qZaQ6S"
        new_pri_key_bytes = b'\xa6\xf8_\xee\x1c\x85\xc5\x95\x8d@\x9e\xfa\x80\x7f\xb6\xe0\xb4u\x12\xb6\xdf\x00\xda4\x98\x8e\xaeR\x89~\xf6\xb5'
        new_pri_key, new_pub_key = ECCipher.generate_key_pair(new_pri_key_bytes)
        print("gen prikey:", new_pri_key)
        print("gen pubkey:", new_pub_key)
        self.assertIsNotNone(new_pri_key)
        self.assertIsNotNone(new_pub_key)

        new_signature = ECCipher.generate_signature(new_pri_key, sample)
        print("new_signature is:", new_signature)
        self.assertIsNotNone(new_signature)

        is_valid_sign = ECCipher.verify_signature(new_pub_key, new_signature, sample)
        print("is valid new_signature:", is_valid_sign)
        self.assertTrue(is_valid_sign)

    def test_generate_key_pair_signature_and_verify_geth(self):
        sample = b"qZaQ6S"
        new_pri_key = b'\xa6\xf8_\xee\x1c\x85\xc5\x95\x8d@\x9e\xfa\x80\x7f\xb6\xe0\xb4u\x12\xb6\xdf\x00\xda4\x98\x8e\xaeR\x89~\xf6\xb5'
        new_pub_key = b'0V0\x10\x06\x07*\x86H\xce=\x02\x01\x06\x05+\x81\x04\x00\n\x03B\x00\x04\\\xfd\xf7\xccD(\x1e\xce`|\x85\xad\xbc*,\x17h.Gj[_N\xadTa\xa9*\xa0x\xff\xb4as\xd1\x94\x9fN\xa3\xe2\xd1fX\xf6\xcf\x8e\xb9+\xab\x0f3\x81\x12\x91\xbdy\xbd\xec\xa6\rZ\x05:\x80'

        print("gen prikey:", new_pri_key)
        print("gen pubkey:", new_pub_key)
        self.assertIsNotNone(new_pri_key)
        self.assertIsNotNone(new_pub_key)

        new_signature = ECCipher.generate_signature(new_pri_key, sample, 'this-is-not-a-secure-password')
        print("new_signature is:", new_signature)
        self.assertIsNotNone(new_signature)

        is_valid_sign = ECCipher.verify_signature(new_pub_key, new_signature, sample)
        print("is valid new_signature:", is_valid_sign)
        self.assertTrue(is_valid_sign)

    def test_load_key_pair_from_private_key(self):

        private_key_file_path = join_with_root(config.wallet.private_key_file)
        password_path = join_with_root(config.wallet.private_key_password_file)

        with open(password_path) as f:
            password = f.read()

        print(password)

        pri_key_string, pub_key_string = ECCipher.geth_load_key_pair_from_private_key(private_key_file_path, password)
        print("pri_key_string:")
        print(pri_key_string)

        print("pub_key_string:")
        print(pub_key_string)

        print("------------------verify is correct pub/pri key--------------------")

        loaded_pub_key = ECCipher.geth_get_public_key_from_private_key(pri_key_string);
        print("loaded_pub_key:" + loaded_pub_key)
        self.assertEqual(pub_key_string, loaded_pub_key)

        # ---------- sign and verify ------------
        data = "testdata"
        new_signature = ECCipher.geth_sign(pri_key_string, data)
        print("new_signature is:" + new_signature)

        is_valid_sign = ECCipher.verify_der_signature(pub_key_string, new_signature, data)
        print("is valid new_signature:" + str(is_valid_sign))
        self.assertTrue(is_valid_sign, "should be success")

        is_valid_sign = ECCipher.verify_der_signature(pub_key_string, new_signature, data+"error")
        print("is valid new_signature:" + str(is_valid_sign))
        self.assertFalse(is_valid_sign, "should be failed")


if __name__ == '__main__':
    unittest.main()
