from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import defer, reactor
from treq.client import HTTPClient
from cpchain.proxy.msg.trade_msg_pb2 import Message

from cpchain.utils import logging
from cpchain.proxy import client
import json
from cpchain import crypto

class MarketClient:
    def __init__(self, priv_keyfile, pub_keyfile):
        self.client = HTTPClient(reactor)
        self.url = 'localhost'  #get url from chain
        self.pub_key = '111' #crypto.ECCipher.get_public_key(pub_keyfile)
        self.priv_key = '222' #crypto.ECCipher.get_private_key(priv_keyfile)
        self.token = 'aaa' #self.login_confirm()

    @inlineCallbacks
    def login(self):
        header = {'Content-Type': 'application/json'}
        data = json.dumps({'public_key': self.pub_key})
        confirm_info = yield self.client.post(url=self.url+'login', headers=header, data=data)
        confirm_info = json.loads(confirm_info)
        if confirm_info['success'] == False:
            print('login failed')
        return confirm_info['message']  #nonce

    @inlineCallbacks
    def login_confirm(self):
        nonce = '213' #self.login()
        signature = 'sig'+nonce #ECCipher.sign(nonce)
        header = {'Content-Type': 'application/json'}
        data = json.dumps({'public_key': self.pub_key, 'code': signature})
        confirm_info = yield self.client.post(self.url+'confirm', headers=header, data=data)
        confirm_info = json.loads(confirm_info)
        if confirm_info['success'] == False:
            print('login failed')
        return confirm_info['message']  #token

    @inlineCallbacks
    def publish_product(self, title, description, price, start_date, end_date):
        header = ['Content-Type: application/json']
        market_key = 'MARKET-KEY: '+self.pub_key
        header.append(market_key)
        market_token = self.token
        header.append(market_token)
        body = {'owner_address': self.pub_key, 'title': title, 'description': description, 'price': price,
                'start_date': start_date, 'end_date': end_date}
        signature = crypto.ECCipher.get_eccipher(self.priv_key).sign(body)
        body['signature'] = signature
        body = str(body)
        confirm = yield self.client.post(self.url+'product', headers=header, data=body)
        return confirm

    @inlineCallbacks
    def change_product_status(self, status):
        header = ['Content-Type: application/json', 'MARKET-KEY: '+self.pub_key, 'MARKET-TOKEN: '+self.token]
        body = str({'status': status})
        confirm = yield self.client.post(url=self.url+'product_change', headers=header, data=body)
        return confirm

    @inlineCallbacks
    def query_product(self, keyword):
        header = ['Content-Type: application/json']
        confirm = yield self.client.get(url=self.url+'procuct', headers=header, params=keyword)
        return confirm

    @inlineCallbacks
    def logout(self):
        header = ['Content-Type: application/json', 'MARKET-KEY: '+self.pub_key, 'MARKET-TOKEN: '+self.token]
        body = {'public_key': self.pub_key, 'token': self.token}
        confirm = yield self.client.post(url=self.url+'logout', headers=header, data=body)
        return confirm

