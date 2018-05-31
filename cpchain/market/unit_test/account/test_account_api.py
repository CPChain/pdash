from tests.market.base_api_test_local import *
from rest_framework.test import APITestCase


class TestAccountApi(LocalBaseApiTest, APITestCase):

    def test_login_and_confirm(self):
        token = self.login()
        self.assertIsNotNone(token, "token should not be empty")

    def test_login_and_confirm_2(self):
        token = self.login2()
        self.assertIsNotNone(token, "token should not be empty")

    def test_update_profiles(self):
        token = self.login()
        self.assertIsNotNone(token, "token should not be empty")

        # update profile
        url = reverse('update_profile')
        print('url:', url)
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
        resp_obj = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(resp_obj)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)

    def test_update_profiles_failed(self):
        token = self.login()
        self.assertIsNotNone(token, "token should not be empty")
        url = reverse('update_profile')
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
        resp_obj = self.client.post(url, data=payload, format='json', **header)
        resp_text = resp_obj.content.decode("utf-8")
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 0)
