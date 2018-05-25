from tests.market.base_api_test import *


class TestAccountApi(BaseApiTest):

    def test_login_and_confirm(self):
        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        self.assertIsNotNone(token, "token should not be empty")

    def test_login_and_confirm_2(self):
        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce2(header)
        token = self._generate_nonce_signature_and_get_token2(header, nonce)

        self.assertIsNotNone(token, "token should not be empty")

    def test_update_profiles(self):

        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)

        # ======= generate nonce signature and confirm =======
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        self.assertIsNotNone(token,"token should not be empty")

        # update profile
        url = '%s/account/v1/profile/update/' % HOST

        payload = {
            'public_key': self.pub_key_string,
            'username': 'username',
            'avatar': 'http://xxx.jpg',
            'email': 'xxx@afdsf.com',
            'gender': 1,
            'mobile': '13800138000',
            'product_number': 0,
        }

        print("update profiles request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.post(url, headers=header, json=payload)

        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        self.assertEqual(parsed_json['status'], 1)

    def test_update_profiles_failed(self):

        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)

        # ======= generate nonce signature and confirm =======
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        self.assertIsNotNone(token,"token should not be empty")

        # update profile
        url = '%s/account/v1/profile/update/' % HOST

        payload = {
            'public_key': self.pub_key_string,
            'username': 333,
            'avatar': 'http://xxx.jpg',
            'email': 'xxx@afdsf.com',
            'gender': "333aa",
            'mobile': '13800138000',
            'product_number': 0,
        }

        print("update profiles request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.post(url, headers=header, json=payload)

        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        self.assertEqual(parsed_json['status'], 0)