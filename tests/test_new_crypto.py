import unittest

from cpchain.utils import join_with_root, config, Encoder
from cpchain.crypto import ECCipher

private_key_file = 'tests/market/assets/UTC--2018-01-25T08-04-38.217120006Z--22114f40ed222e83bbd88dc6cbb3b9a136299a23'
private_key_password_file = 'tests/market/assets/password'


class CryptoTest(unittest.TestCase):

    def setUp(self):
        private_key_file_path = join_with_root(private_key_file)
        password_path = join_with_root(private_key_password_file)
        with open(password_path) as f:
            password = f.read()

        self.private_key_file_path = private_key_file_path
        self.password = password

    def test_load_key(self):
        pri_k, pub_k = ECCipher.load_key_pair(self.private_key_file_path,self.password)
        self.assertIsNotNone(pri_k)
        self.assertIsNotNone(pub_k)

        pri_key = ECCipher.load_private_key(self.private_key_file_path,self.password)
        self.assertIsNotNone(pri_key)

        msg = 'test123'
        sig = ECCipher.create_signature(pri_key, msg)
        print('sig:', sig)
        self.assertIsNotNone(sig)

        create_pub_key = ECCipher.create_public_key_from_private_key(pri_key)
        self.assertIsNotNone(create_pub_key)

        load_pub_key = ECCipher.load_public_key(self.private_key_file_path, self.password)
        self.assertIsNotNone(load_pub_key)

        v1 = ECCipher.verify_sign(load_pub_key, sig, msg)
        self.assertTrue(v1)

        v2 = ECCipher.verify_sign(create_pub_key, sig, msg)
        self.assertTrue(v2)

        addr = ECCipher.get_address_from_public_key(load_pub_key)
        print(addr)
        self.assertIsNotNone(addr)


if __name__ == '__main__':
    unittest.main()
