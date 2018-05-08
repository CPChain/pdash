import unittest

from cpchain.utils import Encoder


class EncoderTest(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.b = b'hello'
        self.string = 'aGVsbG8='

    def test_str_to_base64_byte(self):
        bs = Encoder.str_to_base64_byte(self.string)
        self.assertEqual(self.b, bs)

    def test_bytes_to_base64_str(self):
        self.assertEqual(Encoder.bytes_to_base64_str(self.b), self.string)


if __name__ == '__main__':
    unittest.main()
