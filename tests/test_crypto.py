import unittest

from cpchain.utils import join_with_root, config, Encoder
from cpchain.crypto import ECCipher, ECDERCipher

private_key_file = 'tests/market/assets/UTC--2018-01-25T08-04-38.217120006Z--22114f40ed222e83bbd88dc6cbb3b9a136299a23'
private_key_password_file = 'tests/market/assets/password'


class CryptoTest(unittest.TestCase):

    def test_get_public_key_from_private_key(self):
        private_key_string = "MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAixihD8Ld8YbQICCAAwDAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEG44GNJc06XGWEgbpaGvhB4EgZC/fiBy6TUHehjKFtDI7CE7X26c6yHcLjjDaNDCVYTnSKf12WdzwBbpwbKfM3yOpDessx2Ny6l9UtnDX5rjQjfgNzI61xa+j1SXGIAjd8atlnqULfPnzn2N9TfS9pEY7S6NGrYvhkzbZrejdtM+pl5F/0IJGszP6VSWSZrt+k7NNakfw6uz9VqnBhkIWk+hKJQ="
        public_key_string = "MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAE8s5X7ql5VAr6nfGkkvT5t4uMtSKBivQL6rtwmBZ0C+E2WHR8EqU9X+gElHAaY4b0OUyEqZ17omkqvzaDsNo24g=="

        loaded_pub_key = ECDERCipher.get_public_key_from_private_key(private_key_string);
        print("loaded_pub_key:" + loaded_pub_key)
        self.assertEqual(public_key_string, loaded_pub_key)

    def test_generate_key_pair_signature_and_verify(self):
        private_key_file_path = join_with_root(private_key_file)
        password_path = join_with_root(private_key_password_file)

        with open(password_path) as f:
            password = f.read()

        print(password)
        new_pri_key, pub_key = ECCipher.load_key_pair(private_key_file_path, password)

        sample = b"qZaQ6S"
        print("gen prikey:", new_pri_key)

        self.assertIsNotNone(new_pri_key)

        new_signature = ECCipher.create_signature(new_pri_key, sample)
        print("new_signature is:", new_signature)
        self.assertIsNotNone(new_signature)

        # pub_key = ECCipher.create_public_key(new_pub_key)
        is_valid_sign = ECCipher.verify_sign(pub_key, new_signature, sample)

        print("is valid new_signature:", is_valid_sign)
        self.assertTrue(is_valid_sign)

    def test_load_key_pair_from_private_key_and_verify_signature(self):

        private_key_file_path = join_with_root(private_key_file)
        password_path = join_with_root(private_key_password_file)

        with open(password_path) as f:
            password = f.read()

        print(password)
        pri_key, pub_key = ECCipher.load_key_pair(private_key_file_path, password)

        # ---------- sign and verify ------------
        data = "testdata"
        new_signature = ECCipher.create_signature(pri_key,data)
        print("new_signature is:" + new_signature.hex())

        is_valid_sign = verify_geth_signature(pub_key, new_signature, data)
        print("is valid new_signature:" + str(is_valid_sign))
        self.assertTrue(is_valid_sign, "should be success")

        is_valid_sign = verify_geth_signature(pub_key, new_signature, data + "error")
        print("is valid new_signature:" + str(is_valid_sign))
        self.assertFalse(is_valid_sign, "should be failed")


def verify_geth_signature(pub_key, signature, raw_data_string):
    raw_data = raw_data_string.encode(encoding="utf-8")
    return ECCipher.verify_sign(pub_key, signature, raw_data)


if __name__ == '__main__':
    unittest.main()
