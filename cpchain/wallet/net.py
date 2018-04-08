from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import defer, reactor
from treq.client import HTTPClient
#from cpchain.proxy.msg.trade_msg_pb2 import Message

#from cpchain.utils import logging
#from cpchain.proxy import client
import json
from cpchain import crypto

class MarketClient:
    def __init__(self):
        self.client = HTTPClient(reactor)
        self.url = 'http://localhost:8000/api/v1/'
        self.pub_key = 'MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAE8s5X7ql5VAr6nfGkkvT5t4uMtSKBivQL6rtwmBZ0C+E2WHR8EqU9X+gElHAaY4b0OUyEqZ17omkqvzaDsNo24g==' #crypto.ECCipher.get_public_key(pub_keyfile)
        self.priv_key = '222' #crypto.ECCipher.get_private_key(priv_keyfile)
        self.token = 'aaa' #self.login_confirm()

    @inlineCallbacks
    def login(self):
        header = {'Content-Type': 'application/json'}
        data = {'public_key': self.pub_key}
        resp = yield self.client.post(url=self.url+'login/', headers=header, json=data)
        confirm_info = yield self.client.json_content(resp)
        confirm_info = json.loads(confirm_info)
        if confirm_info['success'] == False:
            print('login failed')
        return confirm_info['message']  #nonce

    @inlineCallbacks
    def login_confirm(self):
        nonce = '213' #self.login()
        signature = crypto.ECCipher.sign(self.priv_key, nonce)
        header = {'Content-Type': 'application/json'}
        data = {'public_key': self.pub_key, 'code': signature}
        resp = yield self.client.post(self.url+'confirm/', headers=header, json=data)
        confirm_info = yield self.client.json_content(resp)
        confirm_info = json.loads(confirm_info)
        if confirm_info['success'] == False:
            print('login failed')
        return confirm_info['message']  #token

    @inlineCallbacks
    def publish_product(self, title, description, price, tags, start_date, end_date, file_md5):
        header = {'Content-Type': 'application/json'}
        header['MARKET-KEY'] = self.pub_key
        header['MARKET-TOKEN'] = 'jjkk'
        data = {'owner_address': self.pub_key, 'title': title, 'description': description, 'price': price,
                'tags': tags, 'start_date': start_date, 'end_date': end_date, 'file_md5:': file_md5}
        signature = crypto.ECCipher.sign(self.priv_key, data)
        data['signature'] = signature
        resp = yield self.client.post(self.url+'product/', headers=header, json=data)
        confirm_info = yield self.client.json_content(resp)
        confirm_info = json.loads(confirm_info)
        if confirm_info['success'] == False:
            print('publish failed')


    @inlineCallbacks
    def change_product_status(self, status):
        header = {'Content-Type': 'application/json', 'MARKET-KEY': self.pub_key, 'MARKET-TOKEN': self.token}
        data = {'status': status}
        confirm_info = yield self.client.post(url=self.url+'product_change', headers=header, json=data)
        if confirm_info['success'] == False:
            print('publish failed')

    @inlineCallbacks
    def query_product(self, keyword):
        header = {'Content-Type': 'application/json'}
        confirm_info = yield self.client.get(url=self.url+'procuct', headers=header, params=keyword)
        confirm_info = json.loads(confirm_info)
        if confirm_info['success'] == False:
            print('query failed')

    @inlineCallbacks
    def logout(self):
        header = {'Content-Type': 'application/json', 'MARKET-KEY': self.pub_key, 'MARKET-TOKEN': self.token}
        data = {'public_key': self.pub_key, 'token': self.token}
        confirm_info = yield self.client.post(url=self.url+'logout', headers=header, json=data)
        confirm_info = json.loads(confirm_info)
        if confirm_info['success'] == False:
            print('logout failed')

if __name__ == '__main__':
    nonce = MarketClient().login()
    print(nonce)
    reactor.run()