from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread

import treq
import json
import os
from cpchain import crypto
import datetime, time

from eth_utils import to_bytes

from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from cpchain.chain.trans import BuyerTrans, SellerTrans, ProxyTrans
from cpchain.chain import poll_chain
from twisted.internet.task import LoopingCall
from cpchain.chain.utils import default_web3
from cpchain.utils import join_with_root, config
from cpchain.chain.models import OrderInfo

from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.client import start_client, download_file
from cpchain.wallet import proxy_request
from cpchain.wallet.fs import publish_file_update, session, FileInfo, decrypt_file_aes
from cpchain.crypto import Encoder


class MarketClient:
    def __init__(self):
        # self.client = HTTPClient(reactor)
        self.url = 'http://192.168.0.132:8083/api/v1/'
        private_key_file_path = join_with_root(config.wallet.private_key_file)
        password_path = join_with_root(config.wallet.private_key_password_file)

        with open(password_path) as f:
            password = f.read()
        self.priv_key, self.pub_key = crypto.ECCipher.geth_load_key_pair_from_private_key(private_key_file_path, password)
        # self.priv_key = 'pvhf7hyFxZWNQJ76gH+24LR1ErbfANo0mI6uUol+9rU='
        # self.pub_key = 'MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEXP33zEQoHs5gfIWtvCosF2guR2pbX06tVGGpKqB4/7Rhc9GUn06j4tFmWPbPjrkrqw8zgRKRvXm97KYNWgU6gA=='
        self.token = ''
        self.nonce = ''
        self.message_hash = ''

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
            signature = crypto.ECCipher.geth_sign(self.priv_key, self.nonce)
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
    def publish_product(self, selected_id, title, description, price, tags, start_date, end_date, file_md5):
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
        signature = crypto.ECCipher.geth_sign(self.priv_key, signature_source)
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
        self.message_hash = confirm_info['data']['market_hash']
        publish_file_update(self.message_hash, selected_id)
        print(self.message_hash)
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
        self.order_id_list = []

    def buy_product(self, msg_hash):
        desc_hash = crypto.Encoder.str_to_base64_byte(msg_hash)
        rsa_key = crypto.RSACipher.load_public_key()
        # rsa_key_list = []
        # for i in rsa_key:
        #     rsa_key_list.append(bytes([i]))
        # product = OrderInfo(desc_hash=b'testdata', seller=b'selleraddress',
        #                            proxy='http://192.168.0.132:8000:api/v1/',
        #                            secondary_proxy='http://192.168.0.132:8000:api/v1/', proxy_value=12, value=30,
        #                            time_allowed=200)
        product = OrderInfo(
            desc_hash=desc_hash, #bytes([0, 1, 2, 3] * 8),
            buyer_rsa_pubkey=rsa_key, #[b'0', b'1', b'2', b'3'] * 128,  #get_rsa_key
            seller=self.buyer.web3.eth.defaultAccount,
            proxy=self.buyer.web3.eth.defaultAccount,
            secondary_proxy=self.buyer.web3.eth.defaultAccount,
            proxy_value=10,
            value=20,
            time_allowed=1000
        )
        print('product:')
        print(product)
        # buyer = BuyerTrans(web3
        # order_id =1

        d = deferToThread(self.buyer.place_order, product)
        def cb(order_id):
            print('order id: ', order_id)
        d.addCallback(cb)
        self.order_id_list.append(self.buyer.place_order(product))
        print('order id: ', self.order_id_list)
        return self.order_id_list

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

    def check_confirm(self):
        if len(self.order_id_list) > 0:
            for current_id in self.order_id_list:
                state = self.buyer.query_order(current_id)[10]
                # If state is Delivered, request to proxy
                if state == 1:
                    print('proxy confirmed')
                    # send request to proxy
                    self.send_request(current_id)
                    return state
                else:
                    print('proxy not confirmed')
                    return state
        else:
            print('no placed order')

    def send_request(self, order_id):
        new_order_info = self.buyer.query_order(order_id)
        message = Message()
        buyer_data = message.buyer_data
        message.type = Message.BUYER_DATA
        buyer_data.order_id = order_id
        buyer_data.seller_addr = to_bytes(hexstr=new_order_info[3])
        buyer_data.buyer_addr = to_bytes(hexstr=new_order_info[2])
        buyer_data.market_hash = new_order_info[0]

        sign_message = SignMessage()
        sign_message.public_key = Encoder.str_to_base64_byte(market_client.pub_key)
        sign_message.data = message.SerializeToString()
        sign_message.signature = crypto.ECCipher.generate_signature(
            Encoder.str_to_base64_byte(market_client.priv_key),
            sign_message.data
        )
        d = start_client(sign_message)

        def buyer_request_proxy_callback(message):
            print("Inside buyer request callback.")
            assert message.type == Message.PROXY_REPLY
            proxy_reply = message.proxy_reply

            if not proxy_reply.error:
                print('file_uuid: %s' % proxy_reply.file_uuid)
                print('AES_key: ')
                print(len(proxy_reply.AES_key))
                print(proxy_reply.AES_key)
                file_dir = os.path.expanduser(config.wallet.download_dir)
                file_path = os.path.join(file_dir, proxy_reply.file_uuid)
                print(file_path)
                decrypted_file = decrypt_file_aes(file_path, proxy_reply.AES_key)
                print('Decrypted file path ' + str(decrypted_file))
                self.confirm_order(order_id)
                self.order_id_list.remove(order_id)
            else:
                print(proxy_reply.error)

        d.addBoth(buyer_request_proxy_callback)




class SellerChainClient:

    def __init__(self):
        self.seller = SellerTrans(default_web3, config.chain.core_contract)
        start_id = self.seller.get_order_num()
        self.monitor = poll_chain.OrderMonitor(start_id, self.seller)

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

    def send_request(self):
        new_order = self.query_new_order()
        if len(new_order) != 0:
            for new_order_id in new_order:
                new_order_info = self.seller.query_order(new_order_id)
                print('In seller send request: new oder infomation:')
                print(new_order_info)
                # send message to proxy
                market_hash = new_order_info[0]
                buyer_rsa_pubkey = new_order_info[1]
                raw_aes_key = session.query(FileInfo.aes_key)\
                    .filter(FileInfo.market_hash == Encoder.bytes_to_base64_str(market_hash))\
                    .all()[0][0]
                print(raw_aes_key)
                encrypted_aes_key = load_der_public_key(buyer_rsa_pubkey, backend=default_backend()).encrypt(
                    raw_aes_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                print(encrypted_aes_key)
                print("Encrypted_aes_key length" + str(len(encrypted_aes_key)))
                storage_type = Message.Storage.IPFS
                ipfs_gateway = "192.168.0.132:5001"
                # File hash is str type
                file_hash = session.query(FileInfo.hashcode)\
                    .filter(FileInfo.market_hash == Encoder.bytes_to_base64_str(market_hash))\
                    .all()[0][0]
                message = Message()
                seller_data = message.seller_data
                message.type = Message.SELLER_DATA
                seller_data.order_id = new_order_id
                seller_data.seller_addr = to_bytes(hexstr=new_order_info[3])
                seller_data.buyer_addr = to_bytes(hexstr=new_order_info[2])
                seller_data.market_hash = market_hash
                seller_data.AES_key = encrypted_aes_key
                storage = seller_data.storage
                storage.type = storage_type
                ipfs = storage.ipfs
                ipfs.file_hash = file_hash.encode('utf-8')
                ipfs.gateway = ipfs_gateway
                sign_message = SignMessage()
                sign_message.public_key = Encoder.str_to_base64_byte(market_client.pub_key)
                sign_message.data = message.SerializeToString()
                sign_message.signature = crypto.ECCipher.generate_signature(
                    Encoder.str_to_base64_byte(market_client.priv_key),
                    sign_message.data
                )
                d = start_client(sign_message)
                d.addBoth(self.seller_deliver_proxy_callback)


    def seller_deliver_proxy_callback(self, message):
        # print('proxy recieved message')
        print("Inside seller request callback.")
        assert message.type == Message.PROXY_REPLY

        proxy_reply = message.proxy_reply

        if not proxy_reply.error:
            print('file_uuid: %s' % proxy_reply.file_uuid)
            print('AES_key: ')
            print(proxy_reply.AES_key)
            # add other action...
        else:
            print(proxy_reply.error)
            # add other action...


class ProxyChainClient:

    def __init__(self):
        self.proxy = ProxyTrans(default_web3, config.chain.core_contract)

    # this methid should be called by proxy
    def proxy_confirm(self):
        print('proxy claim relay')
        self.proxy.claim_relay(5, bytes([0, 1, 2, 3] * 8))




# class SellerProxyClient:
#
#     def __init__(self):
#         self.new_order = []
#         self.new_order_info = ()
#
#     def send_request(self):
#         self.new_order = seller_chain_client.query_new_order()
#         if len(self.new_order) != 0:
#             for i in self.new_order:
#                 self.new_order_info = seller_chain_client.query_order(i)
#                 print(self.new_order_info)


def test_chain_event():
    seller_poll_chain = LoopingCall(seller_chain_client.send_request)
    seller_poll_chain.start(10)


    # print(new_orders)
    # new_orders.addCallbacks()
    # print(order_list)
    # order_info_list = []
    # for i in order_list:
    #     order_info_list.append(seller_chain_client.seller.query_order(i))
    # print(order_info_list)

    buyer_check_confirm = LoopingCall(buyer_chain_client.check_confirm)
    buyer_check_confirm.start(15)


    # from twisted.internet import reactor
    # claim_relay = reactor.callLater(20, proxy_chain_client.proxy_confirm)



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
proxy_chain_client = ProxyChainClient()
# seller_proxy_client = SellerProxyClient()
# market_client.login()

# def buy(msg):
#     print(msg)
#     order_id = market_client.buy_product()
#     print('order id: ', order_id)
#     return order_id
