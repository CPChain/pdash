from rest_framework.test import APITestCase

from tests.market.base_api_test_local import *


class TestUserDataApi(LocalBaseApiTest, APITestCase):

    @staticmethod
    def get_long_id():
        from datetime import datetime
        dt = datetime.today()
        client_id = int(dt.timestamp())
        print(client_id)
        return client_id

    def test_update_upload_file_info(self):
        header = self.get_header()

        client_id = self.get_long_id()
        print(client_id)
        market_hash = "market_hash"

        # ======== test save upload file info in wallet ========
        self._save_upload_file_info(header=header, client_id=client_id)

        # update upload_file_info
        self.update_upload_file_info(header=header, client_id=client_id, market_hash=market_hash)

        # ======== test pull user data in wallet ========
        buyer_files, upload_files = self._pull_user_data(header=header)

    def test_delete_upload_file_info(self):
        header = self.get_header()

        client_id = self.get_long_id()
        print(client_id)
        market_hash = "market_hash"

        # ======== test save upload file info in wallet ========
        self._save_upload_file_info(header=header, client_id=client_id)

        # update upload_file_info
        self.delete_upload_file_info(header=header, client_id=client_id)

        # ======== test pull user data in wallet ========
        buyer_files, upload_files = self._pull_user_data(header=header)
        self.assertEquals(0, len(buyer_files))
        self.assertEquals(0, len(upload_files))

    def test_update_buyer_file_info(self):
        header = self.get_header()

        order_id = self.get_long_id()
        print(order_id)

        # ======== test save buyer file info in wallet ========
        self._save_buyer_file_info(header=header, order_id=order_id)

        # update buyer_file_info
        self.update_buyer_file_info(header=header, order_id=order_id)

        # ======== test pull user data in wallet ========
        self._pull_user_data(header=header)

    def test_delete_buyer_file_info(self):
        header = self.get_header()

        order_id = self.get_long_id()
        print(order_id)

        # ======== test save buyer file info in wallet ========
        self._save_buyer_file_info(header=header, order_id=order_id)

        # delete buyer_file_info
        self.delete_buyer_file_info(header=header, order_id=order_id)

        # ======== test pull user data in wallet ========

        buyer_files, upload_files = self._pull_user_data(header=header)
        self.assertEquals(0, len(buyer_files))
        self.assertEquals(0, len(upload_files))

    def test_query_latest_version(self):
        header = self.get_header()
        self._query_latest_version(header=header)

    def test_add_query_bookmarks(self):
        header = self.get_header()
        # ======== add bookmark =========
        # {"data": {"bookmark": {"market_hash": "market_hash", "name": "name1",
        # "public_key": "34535435",
        # "created": "2018-05-15T09:17:22.147000Z"}}, "status": 1, "message": "success"}
        self._add_bookmark(header=header)

        # ======== query bookmarks =========
        # {"data":
        # {"bookmarks": [{"market_hash": "market_hash", "name": "name1",
        # "public_key": "34535435",
        # "created": "2018-05-15T09:17:22.147000Z"}]}
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

    def _save_upload_file_info(self, header, client_id):
        print("======== save upload file info in wallet ========")

        payload = {"public_key": self.pub_key_string,
                   "hashcode": "hashcode", "path": "path", "size": 1222, "client_id": client_id,
                   "remote_type": "1", "remote_uri": "remote_uri", "is_published": "True",
                   "aes_key": "aes_key", "market_hash": "market_hash", "name": "nnnn"}

        url = reverse('uploaded_file_add')
        response = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(response)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)
        print(resp_text)
        self.assertEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)

    def _save_buyer_file_info(self, header, order_id):
        print("======== save buyer file info in wallet ========")

        payload = {"public_key": self.pub_key_string, "order_id": order_id,
                   "market_hash": "market_hash", "file_uuid": "file_uuid",
                   "file_title": "file_title", "path": "path", "size": 1245,
                   "is_downloaded": "True"}
        url = reverse('buyer_file_add')
        response = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(response)
        print(resp_text)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)
        nonce = parsed_json['message']
        print("nonce:%s" % nonce)

    def _pull_user_data(self, header):
        print("======== pull user data ========")
        url = reverse('pull_user_data')
        response = self.client.get(url, **header)
        print("response:%s" % response)
        resp_text = self.get_response_content(response)
        print(resp_text)
        parsed_json = json.loads(resp_text)

        buyer_files = parsed_json['data']['buyer_files']
        for p in buyer_files:
            print("created:%s" % p["created"])

        upload_files = parsed_json['data']['upload_files']
        for p in upload_files:
            print("created:%s" % p["created"])

        return buyer_files, upload_files

    def _query_latest_version(self, header):
        print("======== query latest version ========")
        params = {"version": 2}
        url = reverse('latest_version')
        response = self.client.get(url, params, **header)
        print("response:%s" % response)
        resp_text = self.get_response_content(response)
        print(resp_text)
        parsed_json = json.loads(resp_text)

        version = parsed_json['data']['version']
        print("version:%s" % version)
        self.assertEquals(0, version)
        status = parsed_json['status']
        self.assertEqual(1, status)

    def _add_bookmark(self, header):
        print("======== add bookmark ========")

        payload = {"public_key": self.pub_key_string,
                   "market_hash": "market_hash", "name": "name1"}
        url = reverse('bookmark_add')
        response = self.client.post(url, data=payload, format='json', **header)
        self.assertEqual(response.status_code, 200)
        resp_text = self.get_response_content(response)
        print(resp_text)
        parsed_json = json.loads(resp_text)
        self.assertEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)

    def _query_bookmarks(self, header):
        print("======== query bookmarks ========")

        url = reverse('bookmark_search')
        response = self.client.get(url, **header)
        print("response:%s" % response)
        resp_text = self.get_response_content(response)
        print(resp_text)
        parsed_json = json.loads(resp_text)

        bookmarks = parsed_json['data']['bookmarks']
        status = parsed_json['status']
        self.assertEqual(1, status)

    def _add_tag(self, header):
        print("======== add tag ========")
        payload = {"tag": "abc11"}

        url = reverse('tag_add')
        response = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(response)
        print(resp_text)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)

        self.assertEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)

    def _query_tags(self, header):
        print("======== query tags ========")

        url = reverse('tag_search')
        response = self.client.get(url, **header)
        print("response:%s" % response)
        resp_text = self.get_response_content(response)
        print(resp_text)
        parsed_json = json.loads(resp_text)

        tags = parsed_json['data']['tags']
        print("tags:%s" % tags)
        status = parsed_json['status']
        self.assertEqual(1, status)

    def update_upload_file_info(self, header, client_id, market_hash):
        print("======== update uploaded_file ========")
        # public_key + client_id -->market_hash + is_published
        payload = {"client_id": client_id, "market_hash": market_hash, "is_published": False}

        url = reverse('uploaded_file_update')
        response = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(response)
        print(resp_text)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)

        self.assertEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)

    def delete_upload_file_info(self, header, client_id):
        print("======== delete uploaded_file ========")
        # public_key + client_id -->upload file info
        payload = {"client_id": client_id}

        url = reverse('uploaded_file_delete')
        response = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(response)
        print(resp_text)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)

        self.assertEqual(parsed_json['status'], 1)
        version = parsed_json['data']['version']
        print("version:%s" % version)
        self.assertGreaterEqual(version, 1)

    def update_buyer_file_info(self, header, order_id):
        print("======== update buyer_file ========")
        # order_id -> is_downloaded
        payload = {"order_id": order_id, "is_downloaded": False}

        url = reverse('buyer_file_update')
        response = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(response)
        print(resp_text)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)

        self.assertEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)

    def delete_buyer_file_info(self, header, order_id):
        print("======== delete buyer_file ========")
        # order_id -> is_downloaded
        payload = {"order_id": order_id}

        url = reverse('buyer_file_delete')
        response = self.client.post(url, data=payload, format='json', **header)
        resp_text = self.get_response_content(response)
        print(resp_text)
        self.assertEqual(response.status_code, 200)
        parsed_json = json.loads(resp_text)

        self.assertEqual(parsed_json['status'], 1)
        message = parsed_json['message']
        print("message:%s" % message)
