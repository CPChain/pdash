from queue import Queue
import logging
import os

from twisted.internet.threads import deferToThread
from twisted.internet import reactor

from eth_utils import to_bytes

from cpchain.utils import config

from cpchain.crypto import Encoder, RSACipher, ECCipher

from cpchain.chain.models import OrderInfo
from cpchain.chain.trans import BuyerTrans, SellerTrans
from cpchain.chain.utils import default_web3
from cpchain.chain.poll_chain import OrderMonitor

from cpchain.wallet.db import BuyerFileInfo
from cpchain.wallet.fs import add_file
from cpchain.wallet.fs import session, FileInfo, decrypt_file_aes

from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.client import start_client

logger = logging.getLogger(__name__)


class Broker:
    def __init__(self, wallet):
        self.wallet = wallet
        # order_queue: info, ready_order_queue: info, bought_order_queue: id, confirmed_order: id
        self.order_queue = Queue()
        self.bought_order_queue = Queue()
        self.ready_order_queue = Queue()
        self.confirmed_order_queue = Queue()
        self.buyer = BuyerTrans(default_web3, config.chain.core_contract)
        self.seller = SellerTrans(default_web3, config.chain.core_contract)

class Monitor:
    def __init__(self, broker):
        self.broker = broker
        start_id = self.broker.seller.get_order_num()
        self.chain_monitor = OrderMonitor(start_id, self.broker.seller)

    # get new order info from chain through web3
    # order list: [{order_id: (xxx, xxx, xxx)}, {order_id: (xxx, xxx, xxx)}]
    def get_new_order_info(self):
        new_order_id_list = self.chain_monitor.get_new_order()
        new_order_info_list = []
        for current_id in new_order_id_list:
            new_order_info_list.append({current_id: self.broker.seller.query_order(current_id)})
        return new_order_info_list

    # this method should be called periodically in the main thread(reactor)
    def monitor_new_order(self):
        new_order_list = deferToThread(self.get_new_order_info)

        def add_order(order_list):
            for current_order in order_list:
                self.broker.order_queue.put(current_order)

        new_order_list.addCallback(add_order)
        return self.broker.order_queue

    # batch process
    def query_order_state(self, order_id_list):
        unready_order_list = []
        for current_id in order_id_list:
            state = self.broker.buyer.query_order(current_id)[10]
            if state == 1:
                order_info = {current_id: self.broker.buyer.query_order(current_id)}
                self.broker.ready_order_queue.put(order_info)
            else:
                unready_order_list.append(current_id)
        return unready_order_list

    def monitor_ready_order(self):
        bought_order_list = []
        while True:
            if self.broker.bought_order_queue.empty():
                break
            else:
                order = self.broker.bought_order_queue.get()
                bought_order_list.append(order)

        d_unready_order = deferToThread(self.query_order_state, bought_order_list)

        def reset_bought_order_queue(unready_order_list):
            for current_id in unready_order_list:
                self.broker.bought_order_queue.put(current_id)

        d_unready_order.addCallback(reset_bought_order_queue)

    def confirm_order(self, order_id_list):
        for current_id in order_id_list:
            self.broker.buyer.confirm_order(current_id)

    def monitor_confirmed_order(self):
        confirmed_order_list = []
        while True:
            if self.broker.confirmed_order_queue.empty():
                break
            else:
                order_id = self.broker.confirmed_order_queue.get()
                confirmed_order_list.append(order_id)
        reactor.callInThread(self.monitor_confirmed_order, confirmed_order_list)


class Handler:
    def __init__(self, broker):
        self.broker = broker

    def buy_product(self, msg_hash, file_title):
        # fixme: format of hash value need to change
        desc_hash = Encoder.str_to_base64_byte(msg_hash)
        rsa_key = RSACipher.load_public_key()
        product = OrderInfo(
            desc_hash=desc_hash,
            buyer_rsa_pubkey=rsa_key,
            seller=self.broker.buyer.web3.eth.defaultAccount,
            # fixme: proxy should not be seller
            proxy=self.broker.buyer.web3.eth.defaultAccount,
            secondary_proxy=self.broker.buyer.web3.eth.defaultAccount,
            proxy_value=10,
            value=20,
            time_allowed=1000
        )
        d_placed_order = deferToThread(self.broker.buyer.place_order, product)

        def add_bought_order(order_id):
            self.broker.bought_order_queue.put(order_id)
            new_buyer_file_info = BuyerFileInfo(order_id=order_id,
                                                market_hash=Encoder.bytes_to_base64_str(desc_hash),
                                                file_title=file_title, is_downloaded=False)
            add_file(new_buyer_file_info)
            # fixme: update UI pane
            # self.update_treasure_pane()

        d_placed_order.addCallback(add_bought_order)

        return self.broker.bought_order_queue

    def seller_send_request(self, order_info):
        order_id = list(order_info.keys())[0]
        new_order_info = order_info[order_id]
        market_hash = new_order_info[0]
        buyer_rsa_pubkey = new_order_info[1]
        raw_aes_key = session.query(FileInfo.aes_key) \
            .filter(FileInfo.market_hash == Encoder.bytes_to_base64_str(market_hash)) \
            .all()[0][0]
        # print(raw_aes_key)

        # fixme
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
        sign_message.public_key = Encoder.str_to_base64_byte(
            self.broker.wallet.market_client.pub_key)
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.generate_signature(
            Encoder.str_to_base64_byte(self.broker.wallet.market_client.priv_key),
            sign_message.data
        )
        d = start_client(sign_message)

        def seller_deliver_proxy_callback(message):
            # print('proxy recieved message')
            logger.debug("Inside seller request callback.")
            assert message.type == Message.PROXY_REPLY

            proxy_reply = message.proxy_reply

            if not proxy_reply.error:
                logger.debug('file_uuid: %s' % proxy_reply.file_uuid)
                logger.debug('AES_key: ')
                logger.debug(proxy_reply.AES_key)
                # add other action...
            else:
                logger.debug(proxy_reply.error)
                # add other action...

        d.addCallback(seller_deliver_proxy_callback)

    def handle_new_order(self):
        while True:
            if self.broker.order_queue.empty():
                break

            else:
                order_info = self.broker.order_queue.get()
                self.seller_send_request(order_info)

    def buyer_send_request(self, order_info):
        order_id = list(order_info.keys())[0]
        new_order_info = order_info[order_id]
        message = Message()
        buyer_data = message.buyer_data
        message.type = Message.BUYER_DATA
        buyer_data.order_id = order_id
        buyer_data.seller_addr = to_bytes(hexstr=new_order_info[3])
        buyer_data.buyer_addr = to_bytes(hexstr=new_order_info[2])
        buyer_data.market_hash = new_order_info[0]

        sign_message = SignMessage()
        sign_message.public_key = Encoder.str_to_base64_byte(
            self.broker.wallet.market_client.pub_key)
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.generate_signature(
            Encoder.str_to_base64_byte(self.broker.wallet.market_client.priv_key),
            sign_message.data
        )
        d = start_client(sign_message)

        def update_buyer_db(file_uuid, file_path):
            market_hash = Encoder.bytes_to_base64_str(new_order_info[0])
            session.query(BuyerFileInfo).filter(BuyerFileInfo.order_id == order_id). \
                update({BuyerFileInfo.market_hash: market_hash,
                        BuyerFileInfo.is_downloaded: True,
                        BuyerFileInfo.file_uuid: file_uuid,
                        BuyerFileInfo.path: file_path,
                        BuyerFileInfo.size: os.path.getsize(file_path)
                        }, synchronize_session=False)
            session.commit()
            return market_hash

        def buyer_request_proxy_callback(message):
            logger.debug("Inside buyer request callback.")
            assert message.type == Message.PROXY_REPLY
            proxy_reply = message.proxy_reply

            if not proxy_reply.error:
                logger.debug('file_uuid: %s' % proxy_reply.file_uuid)
                logger.debug('AES_key: ')
                logger.debug(len(proxy_reply.AES_key))
                logger.debug(proxy_reply.AES_key)
                file_dir = os.path.expanduser(config.wallet.download_dir)
                file_path = os.path.join(file_dir, proxy_reply.file_uuid)
                logger.debug(file_path)
                decrypted_file = decrypt_file_aes(file_path, proxy_reply.AES_key)
                logger.debug('Decrypted file path ' + str(decrypted_file))

                update_buyer_db(proxy_reply.file_uuid, decrypted_file)
                # self.update_treasure_pane()

                self.broker.confirmed_order_queue.put(order_id)

            else:
                logger.debug(proxy_reply.error)

        d.addCallback(buyer_request_proxy_callback)

    def handle_ready_order(self):
        while True:
            if self.broker.ready_order_queue.empty():
                break
            else:
                order_info = self.broker.ready_order_queue.get()
                self.buyer_send_request(order_info)
