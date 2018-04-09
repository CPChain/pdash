from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import defer, reactor
import treq
# from cpchain.proxy.msg.trade_msg_pb2 import Message
#
# from cpchain.utils import logging
# from cpchain.proxy import client
import json
from cpchain import crypto
import datetime, time

class MarketClient:
    def __init__(self):
        # self.client = HTTPClient(reactor)
        self.url = 'http://localhost:8000/api/v1/'
        self.priv_key, self.pub_key = crypto.ECCipher.generate_der_keys()
        self.token = 'b4d731edee96ff28decd0573a3871895468f5095' #self.login_confirm()

    @staticmethod
    def str_to_timestamp(s):
        return str(int(time.mktime(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timetuple())))

    @inlineCallbacks
    def login(self):
        header = {'Content-Type': 'application/json'}
        data = {'public_key': self.pub_key}
        resp = yield treq.post(url=self.url+'login/', headers=header, json=data)
        confirm_info = yield treq.json_content(resp)
        print(confirm_info)
        if confirm_info['success'] == False:
            print('login failed!')
        print(confirm_info['message'])  # nonce
        return confirm_info['message']

    @inlineCallbacks
    def login_confirm(self):
        nonce = 'qZaQ6S'  #self.login()
        signature = crypto.ECCipher.sign_der(self.priv_key, nonce)
        print(signature)
        header = {'Content-Type': 'application/json'}
        data = {'public_key': self.pub_key, 'code': signature}
        resp = yield treq.post(self.url+'confirm/', headers=header, json=data)
        confirm_info = yield treq.json_content(resp)
        if confirm_info['success'] == False:
            print('login failed')
        print(confirm_info['message'])
        return confirm_info['message']  #token

    @inlineCallbacks
    def publish_product(self, title, description, price, tags, start_date, end_date, file_md5):
        header = {'Content-Type': 'application/json'}
        header['MARKET-KEY'] = self.pub_key
        header['MARKET-TOKEN'] = self.token
        data = {'owner_address': self.pub_key, 'title': title, 'description': description, 'price': price,
                'tags': tags, 'start_date': start_date, 'end_date': end_date, 'file_md5:': file_md5}
        signature_source = str(self.pub_key) + str(title) + str(description) + str(price) \
             + self.str_to_timestamp(start_date) + self.str_to_timestamp(end_date) + str(file_md5)
        signature = crypto.ECCipher.sign(self.priv_key, signature_source)
        data['signature'] = signature
        resp = yield treq.post(self.url+'product/', headers=header, json=data)
        confirm_info = yield treq.json_content(resp)
        if confirm_info['success'] == False:
            print('publish failed')
        if confirm_info['success']:
            print('success')

    @inlineCallbacks
    def change_product_status(self, status):
        header = {'Content-Type': 'application/json', 'MARKET-KEY': self.pub_key, 'MARKET-TOKEN': self.token}
        data = {'status': status}
        resp = yield treq.post(url=self.url+'product_change', headers=header, json=data)
        confirm_info = yield treq.json_content(resp)
        if confirm_info['success'] == False:
            print('publish failed')

    @inlineCallbacks
    def query_product(self, keyword):
        header = {'Content-Type': 'application/json'}
        resp = yield treq.get(url=self.url+'procuct', headers=header, params=keyword)
        confirm_info = treq.json_content(resp)
        if confirm_info['success'] == False:
            print('query failed')

    @inlineCallbacks
    def logout(self):
        header = {'Content-Type': 'application/json', 'MARKET-KEY': self.pub_key, 'MARKET-TOKEN': self.token}
        data = {'public_key': self.pub_key, 'token': self.token}
        resp = yield treq.post(url=self.url+'logout', headers=header, json=data)
        confirm_info = treq.json_content(resp)
        if confirm_info['success'] == False:
            print('logout failed')


# if __name__ == '__main__':
#     mc = MarketClient()
#     nonce = mc.login()
#     token = mc.login_confirm()
#     reactor.run()