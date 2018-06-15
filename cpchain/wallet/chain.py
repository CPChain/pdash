import logging
import os
from queue import Queue

from twisted.internet.threads import deferToThread
from twisted.internet import reactor

from eth_utils import to_bytes

from cpchain.utils import config

from cpchain.crypto import Encoder, RSACipher, ECCipher

from cpchain.chain.models import OrderInfo
from cpchain.chain.agents import BuyerAgent, SellerAgent
from cpchain.chain.utils import default_w3, join_with_root
from cpchain.chain.poll_chain import OrderMonitor

from cpchain.wallet.db import BuyerFileInfo
from cpchain.wallet.fs import add_file
from cpchain.wallet.fs import session, FileInfo, decrypt_file_aes

from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.client import start_client

logger = logging.getLogger(__name__) # pylint: disable=locally-disabled, invalid-name


class Broker:
    def __init__(self, wallet):
        self.wallet = wallet
        # order_queue: info, ready_order_queue: info, bought_order_queue: id, confirmed_order_queue: id
        self.order_queue = Queue()
        self.bought_order_queue = Queue()
        self.ready_order_queue = Queue()
        self.confirmed_order_queue = Queue()
        bin_path = join_with_root(config.chain.contract_bin_path)
        # deploy_contract(bin_path, config.chain.contract_name, default_w3)
        self.buyer = BuyerAgent(default_w3, bin_path, config.chain.contract_name)
        self.seller = SellerAgent(default_w3, bin_path, config.chain.contract_name)
        self.handler = Handler(self)
        self.monitor = Monitor(self)

    # batch process
    def query_order_state(self, order_id_list):
        unready_order_list = []
        for current_id in order_id_list:
            state = self.buyer.query_order(current_id)[10]
            if state == 1:
                order_info = {current_id: self.buyer.query_order(current_id)}
                self.ready_order_queue.put(order_info)
            else:
                unready_order_list.append(current_id)
        return unready_order_list


    def confirm_order(self, order_id_list):
        for current_id in order_id_list:
            self.buyer.confirm_order(current_id)


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
        logger.debug("Encrypted_aes_key length: %s", str(len(encrypted_aes_key)))
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
            self.wallet.market_client.pub_key)
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.generate_signature(
            Encoder.str_to_base64_byte(self.wallet.market_client.priv_key),
            sign_message.data
        )
        d_proxy_reply = start_client(sign_message)

        def seller_deliver_proxy_callback(message):
            # print('proxy recieved message')
            logger.debug("Inside seller request callback.")
            assert message.type == Message.PROXY_REPLY

            proxy_reply = message.proxy_reply

            if not proxy_reply.error:
                logger.debug('file_uuid: %s', proxy_reply.file_uuid)
                logger.debug('AES_key: ')
                logger.debug(proxy_reply.AES_key)
                # add other action...
            else:
                logger.debug(proxy_reply.error)
                # add other action...

        d_proxy_reply.addCallback(seller_deliver_proxy_callback)


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
            self.wallet.market_client.pub_key)
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.generate_signature(
            Encoder.str_to_base64_byte(self.wallet.market_client.priv_key),
            sign_message.data
        )
        d_proxy_reply = start_client(sign_message)

        def update_buyer_db(file_uuid, file_path):
            market_hash = Encoder.bytes_to_base64_str(new_order_info[0])
            session.query(BuyerFileInfo).filter(BuyerFileInfo.order_id == order_id).update(
                {BuyerFileInfo.market_hash: market_hash, BuyerFileInfo.is_downloaded: True,
                 BuyerFileInfo.file_uuid: file_uuid, BuyerFileInfo.path: file_path,
                 BuyerFileInfo.size: os.path.getsize(file_path)}, synchronize_session=False)
            session.commit()
            return market_hash

        def buyer_request_proxy_callback(message):
            logger.debug("Inside buyer request callback.")
            assert message.type == Message.PROXY_REPLY
            proxy_reply = message.proxy_reply
            if not proxy_reply.error:
                logger.debug('file_uuid: %s', proxy_reply.file_uuid)
                logger.debug('AES_key: ')
                logger.debug(len(proxy_reply.AES_key))
                logger.debug(proxy_reply.AES_key)
                file_dir = os.path.expanduser(config.wallet.download_dir)
                file_path = os.path.join(file_dir, proxy_reply.file_uuid)
                logger.debug(file_path)
                decrypted_file = decrypt_file_aes(file_path, proxy_reply.AES_key)
                logger.debug('Decrypted file path: %s', str(decrypted_file))

                update_buyer_db(proxy_reply.file_uuid, decrypted_file)
                # self.update_treasure_pane()

                self.confirmed_order_queue.put(order_id)
            else:
                logger.debug(proxy_reply.error)

        d_proxy_reply.addCallback(buyer_request_proxy_callback)




class Monitor:
    def __init__(self, broker):
        self.broker = broker
        start_id = self.broker.seller.get_order_num()
        self.chain_monitor = OrderMonitor(start_id, self.broker.seller)


    # get new order info from chain through web3
    # order list: [{order_id: (xxx, xxx, xxx)}, {order_id: (xxx, xxx, xxx)}]
    def get_new_order_info(self):
        logger.debug("in get new order info")
        new_order_id_list = self.chain_monitor.get_new_order()
        new_order_info_list = []
        for current_id in new_order_id_list:
            logger.debug("process order: %s", current_id)
            new_order_info_list.append({current_id: self.broker.seller.query_order(current_id)})
            logger.debug("order info got, order id: %s", current_id)
        return new_order_info_list


    # this method should be called periodically in the main thread(reactor)
    def monitor_new_order(self):
        logger.debug("in monitor new order")
        logger.debug("order queue size: %s", self.broker.order_queue.qsize())
        new_order_list = deferToThread(self.get_new_order_info)

        def add_order(order_list):
            for current_order in order_list:
                logger.debug("start to put new order info into queue, current order: %s", current_order)
                self.broker.order_queue.put(current_order)
                logger.debug("order queue size: %s", self.broker.order_queue.qsize())


        new_order_list.addCallback(add_order)
        return self.broker.order_queue


    def monitor_ready_order(self):
        logger.debug("in monitor ready order")
        bought_order_list = []
        while True:
            if self.broker.bought_order_queue.empty():
                break
            else:
                order = self.broker.bought_order_queue.get()
                bought_order_list.append(order)
        if len(bought_order_list) == 0:
            logger.debug("no ready order")
        else:
            d_unready_order = deferToThread(self.broker.query_order_state, bought_order_list)

            def reset_bought_order_queue(unready_order_list):
                for current_id in unready_order_list:
                    self.broker.bought_order_queue.put(current_id)

            d_unready_order.addCallback(reset_bought_order_queue)


    def monitor_confirmed_order(self):
        confirmed_order_list = []
        while True:
            if self.broker.confirmed_order_queue.empty():
                break
            else:
                order_id = self.broker.confirmed_order_queue.get()
                confirmed_order_list.append(order_id)
        reactor.callInThread(self.broker.monitor_confirmed_order, confirmed_order_list)




class Handler:
    def __init__(self, broker):
        self.broker = broker

    def get_address_from_public_key_object(self, pub_key_string):
        pub_key = self.get_public_key(pub_key_string)
        return ECCipher.get_address_from_public_key(pub_key)

    def get_public_key(self, public_key_string):
        pub_key_bytes = Encoder.hex_to_bytes(public_key_string)
        return ECCipher.create_public_key(pub_key_bytes)


    def buy_product(self, msg_hash, file_title, proxy, seller):
        # fixme: format of hash value need to change
        logger.debug("start to buy product")
        seller_addr = self.get_address_from_public_key_object(seller)
        desc_hash = Encoder.str_to_base64_byte(msg_hash)
        rsa_key = RSACipher.load_public_key()
        logger.debug("desc hash: %s", desc_hash)
        product = OrderInfo(
            desc_hash=desc_hash,
            buyer_rsa_pubkey=rsa_key,
            seller=self.broker.buyer.web3.toChecksumAddress(seller_addr),
            # fixme: proxy should not be seller
            proxy=self.broker.buyer.web3.toChecksumAddress(proxy),
            secondary_proxy=self.broker.buyer.web3.toChecksumAddress(proxy),
            proxy_value=10,
            value=20,
            time_allowed=1000
        )
        logger.debug("product info has been created")
        logger.debug("product info: %s", product)
        logger.debug("bought order queue size: %s", self.broker.bought_order_queue.qsize())
        d_placed_order = deferToThread(self.broker.buyer.place_order, product)

        def add_bought_order(order_id):
            logger.debug("order has been placed to chain")
            self.broker.bought_order_queue.put(order_id)
            logger.debug("new order has been put into bought order queue")
            logger.debug("bought order queue size: %s", self.broker.bought_order_queue.qsize())
            logger.debug("start to update local database")
            new_buyer_file_info = BuyerFileInfo(order_id=order_id,
                                                market_hash=Encoder.bytes_to_base64_str(desc_hash),
                                                file_title=file_title, is_downloaded=False)
            add_file(new_buyer_file_info)
            logger.debug("update local db completed")

            # fixme: update UI pane
            # self.update_treasure_pane()

        d_placed_order.addCallback(add_bought_order)

        return self.broker.bought_order_queue


    def handle_new_order(self):
        logger.debug("in handle new order")
        logger.debug("before process new order, order queue size: %s", self.broker.order_queue.qsize())
        while True:
            if self.broker.order_queue.empty():
                logger.debug("no new order")
                break

            else:
                order_info = self.broker.order_queue.get()
                logger.debug("process new order, order info: %s", order_info)
                logger.debug("seller send request to proxy ...")
                # self.broker.seller_send_request(order_info)
        logger.debug("new order process completed, order queue size: %s", self.broker.order_queue.qsize())


    def handle_ready_order(self):
        while True:
            if self.broker.ready_order_queue.empty():
                break
            else:
                order_info = self.broker.ready_order_queue.get()
                self.broker.buyer_send_request(order_info)
