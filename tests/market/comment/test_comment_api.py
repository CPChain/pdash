from tests.market.base_api_test import *
from cpchain.market.market.utils import *

class TestCommentApi(BaseApiTest):

    def test_query_comment_list(self):

        token, market_hash = self.get_token_market_hash()
        self.add_comment_failed(token,market_hash)
        # self.add_comment_success(token, market_hash)

        url = '%s/comment/v1/comment/list/?market_hash=%s' % (HOST,market_hash)
        print("url:", url)
        response = requests.get(url)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        for p in parsed_json['data']:
            print("content:%s" % p["content"])

    def test_add_comment_failed(self):

        token, market_hash = self.get_token_market_hash()
        self.add_comment_failed(token,market_hash)

    # def test_add_comment_success(self):
    #     token, market_hash = self.get_token_market_hash()
    #     self.add_comment_success(token,market_hash)

    def test_query_summary_comment(self):
        token, market_hash = self.get_token_market_hash()

        url = '%s/comment/v1/summary_comment/?market_hash=%s' % (HOST,market_hash)
        summary_comment = requests.get(url)
        print("summary_comment:%s" % summary_comment)
        print(summary_comment.text)
        parsed_json = json.loads(summary_comment.text)
        self.assertEqual(parsed_json['status'], 1)
        print("avg_rating:%s" % parsed_json['data']['avg_rating'])
        self.assertGreaterEqual(parsed_json['data']['avg_rating'],1)

    def get_token_market_hash(self):
        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)

        # ======= generate nonce signature and confirm =======
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        market_hash = self.publish_product(token)
        return token,market_hash

    def publish_product(self, token):
        title = "publish product 12444"
        description = "test12345654654654654"
        price = 9527
        tags = "tag1,tag2"
        start_date = "2018-04-01 10:10:10"
        end_date = "2018-12-10 10:10:10"
        file_md5 = "12345678901234567890"
        url = '%s/product/v1/product/publish/' % HOST
        payload = {'owner_address': self.pub_key_string, 'title': title, 'description': description, 'price': price,
                   'tags': tags, 'start_date': start_date, 'end_date': end_date, 'file_md5': file_md5}
        signature_source = self.pub_key_string + title + description + str(price) + start_date + end_date + file_md5

        new_signature = sign(self.pri_key, signature_source)
        print("new_signature is:" + new_signature.hex())

        payload['signature'] = new_signature.hex()
        print("publish product request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        publish_resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(publish_resp.status_code, 200)
        print(publish_resp.text)
        parsed_json = json.loads(publish_resp.text)
        self.assertEqual(parsed_json['status'], 1)
        print("market_hash:%s" % parsed_json['data']["market_hash"])
        return parsed_json['data']["market_hash"]

    def add_comment_failed(self, token, market_hash):
        url = '%s/comment/v1/comment/add/' % HOST
        payload = {'public_key': self.pub_key_string, 'market_hash':market_hash, 'content':'test111'}
        print("add_comment request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.post(url, headers=header, json=payload)

        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        self.assertEqual(parsed_json['status'], 0)

    def add_comment_success(self, token, market_hash):
        # TODO need create tx record first
        url = '%s/comment/v1/comment/add/' % HOST
        payload = {'public_key': self.pub_key_string, 'market_hash':market_hash, 'content':'test111'}
        print("add_comment request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        response = requests.post(url, headers=header, json=payload)

        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        self.assertEqual(parsed_json['status'], 1)