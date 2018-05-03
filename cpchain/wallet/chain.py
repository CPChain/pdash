from cpchain.crypto import Encoder, RSACipher, ECCipher
from cpchain.chain.models import OrderInfo
from twisted.internet.threads import deferToThread
from cpchain.utils import config
from cpchain.chain.trans import BuyerTrans, SellerTrans
from cpchain.chain.utils import default_web3
from cpchain.wallet.db import BuyerFileInfo
from cpchain.wallet.fs import add_file
from cpchain.chain.poll_chain import OrderMonitor
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from eth_utils import to_bytes
from cpchain.proxy.client import start_client
from cpchain.wallet.fs import session, FileInfo
import queue


class Broker:
    def __init__(self, wallet):
        self.wallet = wallet
        self.order_queue = queue.Queue()
        self.bought_queue = queue.Queue()
        self.buyer = BuyerTrans(default_web3, config.chain.core_contract)
        self.seller = SellerTrans(default_web3, config.chain.core_contract)
        start_id = self.seller.get_order_num()
        self.monitor = OrderMonitor(start_id, self.seller)

        # buyer_chain_client = BuyerChainClient(main_wnd, market_client)
        # seller_chain_client = SellerChainClient(main_wnd, market_client)

    def get_new_order_info(self):
        new_order_id_list = self.monitor.get_new_order()
        new_order_info_list = []
        for current_id in new_order_id_list:
            new_order_info_list.append({current_id: self.seller.query_order(current_id)})
        return new_order_info_list


    def monitor_new_order(self):
        new_order_list = deferToThread(self.get_new_order_info)

        def add_order(order_list):
            for current_order in order_list:
                self.order_queue.put(current_order)

        new_order_list.addCallback(add_order)
        return self.order_queue

    def seller_send_request(self, order_info):
        order_id = list(order_info.keys())[0]
        new_order_info = order_info[order_id]
        market_hash = new_order_info[0]
        buyer_rsa_pubkey = new_order_info[1]
        raw_aes_key = session.query(FileInfo.aes_key) \
            .filter(FileInfo.market_hash == Encoder.bytes_to_base64_str(market_hash)) \
            .all()[0][0]
        # print(raw_aes_key)

        # TODO
        encrypted_aes_key = "encrypted aes key"
        # print(encrypted_aes_key)
        print("Encrypted_aes_key length" + str(len(encrypted_aes_key)))
        storage_type = Message.Storage.IPFS
        ipfs_gateway = config.storage.ipfs.addr
        # File hash is str type
        file_hash = session.query(FileInfo.hashcode) \
            .filter(FileInfo.market_hash == Encoder.bytes_to_base64_str(market_hash)) \
            .all()[0][0]
        message = Message()
        seller_data = message.seller_data
        message.type = Message.SELLER_DATA
        seller_data.order_id = order_id
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
        sign_message.public_key = Encoder.str_to_base64_byte(self.wallet.market_client.pub_key)
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.generate_signature(
            Encoder.str_to_base64_byte(self.wallet.market_client.priv_key),
            sign_message.data
        )
        d = start_client(sign_message)

        def seller_deliver_proxy_callback(message):
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

        d.addCallback(seller_deliver_proxy_callback)


    def handler_new_order(self):
        while True:
            if self.order_queue.empty():
                break

            else:
                order_info = self.order_queue.get()
                self.seller_send_request(order_info)
