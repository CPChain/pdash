from tests.market.base_api_test import *


class TestUserDataApi(BaseApiTest):

    def test_user_data_api(self):

        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)

        # ======= generate nonce signature and confirm =======
        token = self._generate_nonce_signature_and_get_token(header, nonce)

        header["MARKET-KEY"] = self.pub_key_string
        header["MARKET-TOKEN"] = token

        # ======== test save upload file info in wallet ========
        self._save_upload_file_info(header=header)

        # ======== test save buyer file info in wallet ========
        self._save_buyer_file_info(header=header)

        # ======== test query latest version info in wallet ========
        self._query_latest_version(header=header)

        # ======== test pull user data in wallet ========
        self._pull_user_data(header=header)

        # ======== TODO add bookmark =========
        self._add_bookmark(header=header)

        # ======== TODO query bookmarks =========
        self._query_bookmarks(header=header)

        # ======== TODO add tag =========
        self._add_tag(header=header)

        # ======== TODO query tags =========
        self._query_tags(header=header)

    def _login_and_get_nonce(self, header):
        payload = {"public_key": self.pub_key_string}
        url = '%s/account/v1/login/' % HOST
        response = requests.post(url, headers=header, json=payload)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(response.text)
        # print(response.text)
        self.assertEqual(parsed_json['status'], True)
        nonce = parsed_json['message']
        print("nonce:%s" % nonce)
        return nonce

    def _generate_nonce_signature_and_get_token(self, header, nonce):
        url = '%s/account/v1/confirm/' % HOST
        nonce_signature = generate_nonce_signature(self.pri_key_string, nonce)
        payload = {"public_key": self.pub_key_string, "code": nonce_signature}
        # print("confirm request:%s" % payload)
        confirm_resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(confirm_resp.status_code, 200)
        parsed_json = json.loads(confirm_resp.text)
        self.assertEqual(parsed_json['status'], True)
        token = parsed_json['message']
        print("token:%s" % token)
        return token

    def query_product(self, keyword):
        params = {"keyword": keyword}
        url = '%s/product/v1/product/search/' % HOST
        response = requests.get(url, params)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)
        for p in parsed_json:
            print("title:%s" % p["title"])

    def query_es_product(self):
        keyword = "testtile"
        params = {"keyword": keyword}
        url = '%s/product/v1/es_product/search/' % HOST
        response = requests.get(url, params)
        print("products:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

        result = parsed_json['results']
        for p in result:
            print("title:%s" % p["title"])

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
        signature = ECCipher.generate_string_signature(self.pri_key_string, signature_source)
        payload['signature'] = signature
        print("publish product request:%s" % payload)
        header = {"MARKET-KEY": self.pub_key_string, "MARKET-TOKEN": token, 'Content-Type': 'application/json'}
        publish_resp = requests.post(url, headers=header, json=payload)
        self.assertEqual(publish_resp.status_code, 200)
        print(publish_resp.text)
        parsed_json = json.loads(publish_resp.text)
        self.assertEqual(parsed_json['status'], 1)
        print("market_hash:%s" % parsed_json['data']["market_hash"])

    def _save_upload_file_info(self, header):
        print("======== save upload file info in wallet ========")

        payload = {"public_key": self.pub_key_string,
                   "hashcode": "hashcode", "path": "path", "size": 1222,
                   "remote_type": "1", "remote_uri": "remote_uri", "is_published": "True",
                   "aes_key": "aes_key", "market_hash": "market_hash","name": "nnnn"}
        url = '%s/user_data/v1/uploaded_file/' % HOST
        response = requests.post(url, headers=header, json=payload)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(response.text)
        print(response.text)
        self.assertEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)

    def _save_buyer_file_info(self, header):
        print("======== save buyer file info in wallet ========")

        payload = {"public_key": self.pub_key_string, "order_id": 6666,
                   "market_hash": "market_hash", "file_uuid": "file_uuid",
                   "file_title": "file_title", "path": "path", "size": 1245,
                   "is_downloaded": "True"}
        url = '%s/user_data/v1/buyer_file/' % HOST
        response = requests.post(url, headers=header, json=payload)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(response.text)
        print(response.text)
        self.assertEqual(parsed_json['status'], 1)
        nonce = parsed_json['message']
        print("nonce:%s" % nonce)

    def _pull_user_data(self, header):
        print("======== pull user data ========")
        url = '%s/user_data/v1/pull_all/' % HOST
        response = requests.get(url=url, headers=header)
        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

        result = parsed_json['data']['buyer_files']
        for p in result:
            print("created:%s" % p["created"])

    def _query_latest_version(self, header):
        print("======== query latest version ========")
        params = {"version": 2}
        url = '%s/user_data/v1/latest_version/' % HOST
        response = requests.get(url=url, headers=header, params=params)
        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

        version = parsed_json['data']['version']
        print("version:%s" % version)
        status = parsed_json['status']
        self.assertEqual(1,status)

    def _add_bookmark(self, header):
        print("======== add bookmark ========")

        payload = {"public_key": self.pub_key_string,
                   "market_hash": "market_hash", "name": "name1"}
        url = '%s/user_data/v1/bookmark/' % HOST
        response = requests.post(url, headers=header, json=payload)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(response.text)
        print(response.text)
        self.assertEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)

    def _query_bookmarks(self, header):
        print("======== query bookmarks ========")
        url = '%s/user_data/v1/bookmark/' % HOST
        response = requests.get(url=url, headers=header)
        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

        bookmarks = parsed_json['data']['bookmarks']
        print("bookmarks:%s" % bookmarks)
        status = parsed_json['status']
        self.assertEqual(1, status)

    def _add_tag(self,header):
        print("======== add tag ========")
        payload = {"tag": "abc11"}
        url = '%s/user_data/v1/tag/' % HOST
        response = requests.post(url, headers=header, json=payload)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(response.text)
        print(response.text)
        self.assertEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)

    def _query_tags(self,header):
        print("======== query tags ========")
        url = '%s/user_data/v1/tag/' % HOST
        response = requests.get(url=url, headers=header)
        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

        tags = parsed_json['data']['tags']
        print("tags:%s" % tags)
        status = parsed_json['status']
        self.assertEqual(1,status)