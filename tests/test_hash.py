import unittest

from cpchain.utils import SHA256Hash


class HashTest(unittest.TestCase):
    def test_hash(self):
        sha256_hash = SHA256Hash.generate_hash('str')

        self.assertEqual(sha256_hash, 'jCXLNoZGLpqG0og8VoiiL+c4sLvIX0WNLStfP2Z8bVo=')


if __name__ == '__main__':
    unittest.main()
