import unittest

from cpchain.market.api.utils import *
from cpchain.utils import join_with_root,config

private_key_string = "MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAixihD8Ld8YbQICCAAwDAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEG44GNJc06XGWEgbpaGvhB4EgZC/fiBy6TUHehjKFtDI7CE7X26c6yHcLjjDaNDCVYTnSKf12WdzwBbpwbKfM3yOpDessx2Ny6l9UtnDX5rjQjfgNzI61xa+j1SXGIAjd8atlnqULfPnzn2N9TfS9pEY7S6NGrYvhkzbZrejdtM+pl5F/0IJGszP6VSWSZrt+k7NNakfw6uz9VqnBhkIWk+hKJQ="
public_key_string = "MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAE8s5X7ql5VAr6nfGkkvT5t4uMtSKBivQL6rtwmBZ0C+E2WHR8EqU9X+gElHAaY4b0OUyEqZ17omkqvzaDsNo24g=="


class UtilsTest(unittest.TestCase):

    def test_generate_keys(self):
        new_pri_key, new_pub_key = generate_keys()
        print("gen prikey:", new_pri_key)
        print("gen pubkey:", new_pub_key)
        self.assertIsNotNone(new_pri_key)
        self.assertIsNotNone(new_pub_key)

    def test_sign_and_verify1(self):
        sample = "qZaQ6S"

        print("pri key:", private_key_string)
        print("pub key:", public_key_string)
        print("sample:", sample)
        new_signature = sign_der(private_key_string, sample)
        print("new_signature is:", new_signature)
        self.assertIsNotNone(new_signature)

        is_valid_sign = verify_signature(public_key_string, new_signature, sample)
        print("is valid new_signature:", is_valid_sign)
        self.assertTrue(is_valid_sign)

    def test_sign_and_verify_2(self):
        data = "MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAE8s5X7ql5VAr6nfGkkvT5t4uMtSKBivQL6rtwmBZ0C+E2WHR8EqU9X+gElHAaY4b0OUyEqZ17omkqvzaDsNo24g==6666677881224152254861015225486101234567890"
        new_signature = sign_der(private_key_string, data)
        print("new_signature is:" + new_signature)

        is_valid_sign = verify_signature(public_key_string, new_signature, data)
        print("is valid new_signature:" + str(is_valid_sign))

    def test_get_public_key_from_private_key(self):
        loaded_pub_key = ECCipher.get_public_key_from_private_key(private_key_string);
        print("loaded_pub_key:" + loaded_pub_key)
        self.assertEqual(public_key_string, loaded_pub_key)

    def test_verify_signature(self):
        # piks = "MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAixihD8Ld8YbQICCAAwDAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEG44GNJc06XGWEgbpaGvhB4EgZC/fiBy6TUHehjKFtDI7CE7X26c6yHcLjjDaNDCVYTnSKf12WdzwBbpwbKfM3yOpDessx2Ny6l9UtnDX5rjQjfgNzI61xa+j1SXGIAjd8atlnqULfPnzn2N9TfS9pEY7S6NGrYvhkzbZrejdtM+pl5F/0IJGszP6VSWSZrt+k7NNakfw6uz9VqnBhkIWk+hKJQ="
        pub_key = "MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEddc0bkalTTqEiUu6g884be4ghnMGYWfyJHTSjEMrE+zCRq6T1VHF21vJCPXs+YBvtyPJ7mJiRyHw/2FH3b8unQ=="
        source_data = "MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEddc0bkalTTqEiUu6g884be4ghnMGYWfyJHTSjEMrE+zCRq6T1VHF21vJCPXs+YBvtyPJ7mJiRyHw/2FH3b8unQ==testtestdata1315225486101522548610123456"
        new_signature = "MEYCIQDer/bauZFVnWA4LuB0sfx16cWeZRkk68CpQCT2yUDsdgIhAK0ow609LVLUyDruUeWrGNQNt7Ugch91AcxpEuMhs5yl"

        is_valid_sign = verify_signature(pub_key, new_signature, source_data)
        print("test_verify_sign:" + str(is_valid_sign))
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
        new_signature = sign(pri_key_string, data)
        print("new_signature is:" + new_signature)

        is_valid_sign = verify_signature(pub_key_string, new_signature, data)
        print("is valid new_signature:" + str(is_valid_sign))
        self.assertTrue(is_valid_sign, "should be success")

        is_valid_sign = verify_signature(pub_key_string, new_signature, data+"error")
        print("is valid new_signature:" + str(is_valid_sign))
        self.assertFalse(is_valid_sign, "should be failed")


if __name__ == '__main__':
    unittest.main()
