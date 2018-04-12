from twisted.internet.defer import inlineCallbacks
import treq
import json
from cpchain import crypto
import datetime, time
from cpchain.chain.trans import BuyerTrans

# from twisted.python.log import startLogging
# import sys
# startLogging(sys.stdout)


class MarketClient:
    def __init__(self):
        # self.client = HTTPClient(reactor)
        self.url = 'http://192.168.0.132:8000/api/v1/'
        self.priv_key = 'MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAijHDc56pWCBQICCAAwDAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEAFP6mba6NQbUCmI2SSJdw0EgZDgxdLy3ToxSgS3PDKrcUvB0Ti6KO1OuYfsHetgUX3r4m1kacI73ooKJ9UvuPuOG7czcuxr6Zk/SOuicpxU0pticj0ZRZh4wRdbP+3qScZ8h7MapoZq0Q/sO7pYJoFg+MQPD5fMA5B7u9gLzxlF697rbWtuT17e7RmKPhE+hIEBHu6Z/blzrfT+o+QDPpPo1oE='
        self.pub_key = 'MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEddc0bkalTTqEiUu6g884be4ghnMGYWfyJHTSjEMrE+zCRq6T1VHF21vJCPXs+YBvtyPJ7mJiRyHw/2FH3b8unQ=='
        self.token = 'eef5293f97a64c26d874507d0ef6dc5ba9bed2bc'
        self.nonce = 'gZM6Hg'

    @staticmethod
    def str_to_timestamp(s):
        return s #str(int(time.mktime(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timetuple())))


    @inlineCallbacks
    def login(self):
        header = {'Content-Type': 'application/json'}
        data = {'public_key': self.pub_key}
        try:
            resp = yield treq.post(url=self.url+'login/', headers=header, json=data, persistent=False)
            confirm_info = yield treq.json_content(resp)
            print(confirm_info)
            # if confirm_info['success'] == False:
            #     print('login failed!')
            # print(confirm_info['message'])  # nonce
            self.nonce = confirm_info['message']
            print('login succeed')
        except Exception as err:
            print(err)

        try:
            signature = crypto.ECCipher.sign_der(self.priv_key, self.nonce)
            # print(signature)
            header_confirm = {'Content-Type': 'application/json'}
            data_confirm = {'public_key': self.pub_key, 'code': signature}
            # import treq
            resp = yield treq.post(self.url + 'confirm/', headers=header_confirm, json=data_confirm, persistent=False)

            confirm_info = yield treq.json_content(resp)
            print(confirm_info)
            # if confirm_info['success'] == False:
            #     print('login failed')
            # print(confirm_info['message'])
            self.token = confirm_info['message']
            print('login confirmed')
        except Exception as err:
            print(err)
        return confirm_info['message']


    # @inlineCallbacks
    # def login_confirm(self):
    #     # self.nonce = yield self.login()
    #     signature = crypto.ECCipher.sign_der(self.priv_key, self.nonce)
    #     # print(signature)
    #     header = {'Content-Type': 'application/json'}
    #     data = {'public_key': self.pub_key, 'code': signature}
    #     import treq
    #     resp = yield treq.post(self.url+'confirm/', headers=header, json=data)
    #     confirm_info = yield treq.json_content(resp)
    #     print(confirm_info)
    #     # if confirm_info['success'] == False:
    #     #     print('login failed')
    #     # print(confirm_info['message'])
    #     self.token = confirm_info['message']
    #     print('login confirmed')
    #     return confirm_info['message']  #token

    @inlineCallbacks
    def publish_product(self, title, description, price, tags, start_date, end_date, file_md5):
        header = {'Content-Type': 'application/json'}
        header['MARKET-KEY'] = self.pub_key
        header['MARKET-TOKEN'] = self.token
        data = {'owner_address': self.pub_key, 'title': title, 'description': description, 'price': price,
                'tags': tags, 'start_date': start_date, 'end_date': end_date, 'file_md5': file_md5}
        # print(json.dumps(data))
        # print(self.token)
        signature_source = str(self.pub_key) + str(title) + str(description) + str(price) + MarketClient.str_to_timestamp(start_date) + MarketClient.str_to_timestamp(end_date) + str(file_md5)
        # print(self.priv_key)
        # print(self.pub_key)
        # print(signature_source)
        signature = crypto.ECCipher.sign_der(self.priv_key, signature_source)
        data['signature'] = signature
        # print(signature)
        # print(data)
        import treq
        resp = yield treq.post(self.url + 'product/publish/', headers=header, json=data)
        confirm_info = yield treq.json_content(resp)
        print(confirm_info)
        # if confirm_info['message'] == 'success':
        #     print('publish ')
        # if confirm_info['success']:
        #     print('success')
        print('publish succeed')
        return confirm_info['status']

    @inlineCallbacks
    def change_product_status(self, status):
        header = {'Content-Type': 'application/json', 'MARKET-KEY': self.pub_key, 'MARKET-TOKEN': self.token}
        data = {'status': status}
        import treq
        resp = yield treq.post(url=self.url+'product_change', headers=header, json=data)
        confirm_info = yield treq.json_content(response=resp)
        if confirm_info['success'] == False:
            print('publish failed')

    @inlineCallbacks
    def query_product(self, keyword):
        header = {'Content-Type': 'application/json'}
        import treq
        url = self.url + 'product/search/?keyword=' + str(keyword)
        # print("url:%s",url)
        resp = yield treq.get(url=url, headers=header)
        # print(resp)
        confirm_info = yield treq.json_content(resp)
        print(confirm_info)
        return confirm_info

    @inlineCallbacks
    def logout(self):
        header = {'Content-Type': 'application/json', 'MARKET-KEY': self.pub_key, 'MARKET-TOKEN': self.token}
        data = {'public_key': self.pub_key, 'token': self.token}
        import treq
        resp = yield treq.post(url=self.url+'logout', headers=header, json=data)
        confirm_info = yield treq.json_content(resp)
        print(confirm_info)
        # if confirm_info['success'] == False:
        #     print('logout failed')

    def buy_product(self):
        product = OrderInfo

# if __name__ == '__main__':
    # mc = MarketClient()
    # mc.login()
    # mc.login_confirm()
    # mc.publish_product(title='test', description='testdata', price=13, tags='temp', start_date='2018-04-01 10:10:10', end_date='2018-04-01 10:10:10', file_md5='123456')
    # mc.query_product('test')
    # mc.logout()
    # from twisted.internet import reactor
    # reactor.run()
    # pri_key = 'MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAijHDc56pWCBQICCAAwDAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEAFP6mba6NQbUCmI2SSJdw0EgZDgxdLy3ToxSgS3PDKrcUvB0Ti6KO1OuYfsHetgUX3r4m1kacI73ooKJ9UvuPuOG7czcuxr6Zk/SOuicpxU0pticj0ZRZh4wRdbP+3qScZ8h7MapoZq0Q/sO7pYJoFg+MQPD5fMA5B7u9gLzxlF697rbWtuT17e7RmKPhE+hIEBHu6Z/blzrfT+o+QDPpPo1oE='
    # pub_key = 'MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEddc0bkalTTqEiUu6g884be4ghnMGYWfyJHTSjEMrE+zCRq6T1VHF21vJCPXs+YBvtyPJ7mJiRyHw/2FH3b8unQ=='
    # sig = 'MEYCIQD/bAkaxXqn3nk6nDVdR1Jf4dUrmk7nYbNEwMYRiHLCJQIhAOtYxJmcqVTFznPf98cHUHaGIIYk3XLUAV0MomJl05iG'
    # source = 'MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEddc0bkalTTqEiUu6g884be4ghnMGYWfyJHTSjEMrE+zCRq6T1VHF21vJCPXs+YBvtyPJ7mJiRyHw/2FH3b8unQ==testtestdata1315225486101522548610123456'
    # res = crypto.ECCipher.verify_der_signature(pub_key, sig, source)
    # print(res)
    # pub_key = crypto.ECCipher.get_public_key_from_private_key('MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAijHDc56pWCBQICCAAwDAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEAFP6mba6NQbUCmI2SSJdw0EgZDgxdLy3ToxSgS3PDKrcUvB0Ti6KO1OuYfsHetgUX3r4m1kacI73ooKJ9UvuPuOG7czcuxr6Zk/SOuicpxU0pticj0ZRZh4wRdbP+3qScZ8h7MapoZq0Q/sO7pYJoFg+MQPD5fMA5B7u9gLzxlF697rbWtuT17e7RmKPhE+hIEBHu6Z/blzrfT+o+QDPpPo1oE=')
    # print(pub_key)
    # print('MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEddc0bkalTTqEiUu6g884be4ghnMGYWfyJHTSjEMrE+zCRq6T1VHF21vJCPXs+YBvtyPJ7mJiRyHw/2FH3b8unQ==')

market_client = MarketClient()
# market_client.login()

def hoge(msg):
    print(msg)
