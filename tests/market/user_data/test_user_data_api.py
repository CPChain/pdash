from tests.market.base_api_test import *


class TestUserDataApi(BaseApiTest):

    def test_upload_user_data_api(self):
        header = self.get_header()

        # ======== test save upload file info in wallet ========
        self._save_upload_file_info(header=header)

        # ======== test save buyer file info in wallet ========
        self._save_buyer_file_info(header=header)

        # ======== test pull user data in wallet ========
        self._pull_user_data(header=header)

    def test_query_latest_version(self):
        header = self.get_header()
        self._query_latest_version(header=header)

    def test_add_query_bookmarks(self):
        header = self.get_header()
        # ======== add bookmark =========
        # {"data": {"bookmark": {"market_hash": "market_hash", "name": "name1", "public_key": "BFz998xEKB7OYHyFrbwqLBdoLkdqW19OrVRhqSqgeP+0YXPRlJ9Oo+LRZlj2z465K6sPM4ESkb15veymDVoFOoA=", "created": "2018-05-15T09:17:22.147000Z"}}, "status": 1, "message": "success"}
        self._add_bookmark(header=header)

        # ======== query bookmarks =========
        # {"data":
        # {"bookmarks": [{"market_hash": "market_hash", "name": "name1", "public_key": "BFz998xEKB7OYHyFrbwqLBdoLkdqW19OrVRhqSqgeP+0YXPRlJ9Oo+LRZlj2z465K6sPM4ESkb15veymDVoFOoA=", "created": "2018-05-15T09:17:22.147000Z"}]}
        # ,"status": 1, "message": "success"}
        self._query_bookmarks(header=header)

    def test_add_query_tags(self):
        header = self.get_header()
        # ======== add tag =========
        self._add_tag(header=header)

        # ======== query tags =========
        self._query_tags(header=header)

    def get_header(self):
        header = {'Content-Type': 'application/json'}
        nonce = self._login_and_get_nonce(header)
        # ======= generate nonce signature and confirm =======
        token = self._generate_nonce_signature_and_get_token(header, nonce)
        header["MARKET-KEY"] = self.pub_key_string
        header["MARKET-TOKEN"] = token
        return header

    def _save_upload_file_info(self, header):
        print("======== save upload file info in wallet ========")

        payload = {"public_key": self.pub_key_string,
                   "hashcode": "hashcode", "path": "path", "size": 1222,
                   "remote_type": "1", "remote_uri": "remote_uri", "is_published": "True",
                   "aes_key": "aes_key", "market_hash": "market_hash", "name": "nnnn"}
        url = '%s/user_data/v1/uploaded_file/add/' % HOST
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
        url = '%s/user_data/v1/buyer_file/add/' % HOST
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
        self.assertEqual(1, status)

    def _add_bookmark(self, header):
        print("======== add bookmark ========")

        payload = {"public_key": self.pub_key_string,
                   "market_hash": "market_hash", "name": "name1"}
        url = '%s/user_data/v1/bookmark/add/' % HOST
        response = requests.post(url, headers=header, json=payload)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(response.text)
        print(response.text)
        self.assertEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)

    def _query_bookmarks(self, header):
        print("======== query bookmarks ========")
        url = '%s/user_data/v1/bookmark/search/' % HOST
        response = requests.get(url=url, headers=header)
        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

        bookmarks = parsed_json['data']['bookmarks']
        status = parsed_json['status']
        self.assertEqual(1, status)

    def _add_tag(self, header):
        print("======== add tag ========")
        payload = {"tag": "abc11"}
        url = '%s/user_data/v1/tag/add/' % HOST
        response = requests.post(url, headers=header, json=payload)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(response.text)
        print(response.text)
        self.assertEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)

    def _query_tags(self, header):
        print("======== query tags ========")
        url = '%s/user_data/v1/tag/search/' % HOST
        response = requests.get(url=url, headers=header)
        print("response:%s" % response)
        print(response.text)
        parsed_json = json.loads(response.text)

        tags = parsed_json['data']['tags']
        print("tags:%s" % tags)
        status = parsed_json['status']
        self.assertEqual(1, status)
