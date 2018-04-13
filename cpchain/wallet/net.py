from twisted.internet.defer import inlineCallbacks
import treq
import json
from cpchain import crypto
import datetime, time
from cpchain.chain.trans import BuyerTrans, SellerTrans
from cpchain.chain import poll_chain
from twisted.internet.task import LoopingCall
from cpchain.chain.utils import default_web3
from cpchain import config
from cpchain.chain.models import OrderInfo


class MarketClient:
    def __init__(self):
        # self.client = HTTPClient(reactor)
        self.url = 'http://192.168.0.132:8083/api/v1/'
        self.priv_key = 'pvhf7hyFxZWNQJ76gH+24LR1ErbfANo0mI6uUol+9rU='
        self.pub_key = 'MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEXP33zEQoHs5gfIWtvCosF2guR2pbX06tVGGpKqB4/7Rhc9GUn06j4tFmWPbPjrkrqw8zgRKRvXm97KYNWgU6gA=='
        self.token = 'eef5293f97a64c26d874507d0ef6dc5ba9bed2bc'
        self.nonce = 'gZM6Hg'

    @staticmethod
    def str_to_timestamp(s):
        return s #str(int(time.mktime(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timetuple())))

    @inlineCallbacks
    def login(self):
        header = {'Content-Type': 'application/json'}
        data = {'public_key': self.pub_key}
        # import treq
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
            # print('in')
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
        # import treq
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
        # import treq
        url = self.url + 'product/search/?keyword=' + str(keyword)
        # print("url:%s",url)
        resp = yield treq.get(url=url, headers=header)
        # print(resp)
        confirm_info = yield treq.json_content(resp)
        print('product info: ')
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


class BuyerChainClient:

    def __init__(self):
        self.buyer = BuyerTrans(default_web3, config.chain.core_contract)

    def buy_product(self, msg):
        print(msg)
        # product = OrderInfo(desc_hash=b'testdata', seller=b'selleraddress',
        #                            proxy='http://192.168.0.132:8000:api/v1/',
        #                            secondary_proxy='http://192.168.0.132:8000:api/v1/', proxy_value=12, value=30,
        #                            time_allowed=200)
        product = OrderInfo(
            desc_hash=bytes([0, 1, 2, 3] * 8),
            seller=self.buyer.web3.eth.defaultAccount,
            proxy=self.buyer.web3.eth.defaultAccount,
            secondary_proxy=self.buyer.web3.eth.defaultAccount,
            proxy_value=10,
            value=20,
            time_allowed=100
        )
        print('product:')
        print(product)
        # buyer = BuyerTrans(web3
        # order_id =1
        order_id = self.buyer.place_order(product)
        print('order id: ', order_id)
        return order_id

    def withdraw_order(self, order_id):
        # tx_hash = '0xand..'
        tx_hash = self.buyer.withdraw_order(order_id)
        print('withdraw order: ', tx_hash)
        return tx_hash

    def confirm_order(self, order_id):
        # tx_hash = '0xand..'
        tx_hash = self.buyer.confirm_order(order_id)
        print('confirm order: ', tx_hash)
        return tx_hash

    def dispute(self, order_id):
        # tx_hash = '0xand..'
        tx_hash = self.buyer.dispute(order_id)
        print('start a dispute: ', tx_hash)
        return tx_hash

    def check_confirm(self, order_id):
        state = self.buyer.query_order(order_id)[9]
        if state == 3:
            print('proxy confirmed')
            return state
        else:
            print('proxy not confirmed')
            return state


class SellerChainClient:

    def __init__(self):
        self.seller = SellerTrans(default_web3, config.chain.core_contract)
        self.monitor = poll_chain.OrderMonitor(1, self.seller)

    def query_new_order(self):
        # new_order_list = [1,2,3,4]
        new_order_list = self.monitor.get_new_order()
        print('new orders: ', new_order_list)
        return new_order_list

    def claim_timeout(self, order_id):
        tx_hash = '0xand..'
        # tx_hash = self.seller.claim_timeout(order_id)
        print('claim timeout: ', tx_hash)
        return tx_hash



def test_chain_event():
    seller_poll_chain = LoopingCall(seller_chain_client.query_new_order)
    seller_poll_chain.start(10)
    # print(order_list)
    # order_info_list = []
    # for i in order_list:
    #     order_info_list.append(seller_chain_client.seller.query_order(i))
    # print(order_info_list)

    buyer_check_confirm = LoopingCall(buyer_chain_client.check_confirm, 1)
    buyer_check_confirm.start(15)


    # from twisted.internet import reactor
    # buy_product = reactor.callLater(1, buyer_chain_client.buy_product, 'hi')
    # withdraww_order = reactor.callLater(5, buyer_chain_client.withdraw_order, 1)
    # confirm_order = reactor.callLater(10, buyer_chain_client.confirm_order, 1)
    # dispute = reactor.callLater(15, buyer_chain_client.dispute, 1)
    # timeout = reactor.callLater(20, seller_chain_client.claim_timeout, 1)



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
buyer_chain_client = BuyerChainClient()
seller_chain_client = SellerChainClient()
# market_client.login()

# def buy(msg):
#     print(msg)
#     order_id = market_client.buy_product()
#     print('order id: ', order_id)
#     return order_id