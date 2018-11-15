import logging
import os
import asyncio
import json

from queue import Queue

from twisted.internet.threads import deferToThread
from twisted.internet import reactor

from twisted.internet import defer

from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from cpchain.utils import config, join_with_root, join_with_rc

from cpchain.crypto import Encoder, RSACipher, ECCipher

from cpchain.chain.models import OrderInfo
from cpchain.chain.agents import BuyerAgent, SellerAgent
from cpchain.chain.utils import default_w3
from cpchain.chain.poll_chain import OrderMonitor

from cpchain.wallet.db import BuyerFileInfo
from cpchain.wallet.fs import add_file
from cpchain.wallet.utils import eth_addr_to_string, get_address_from_public_key_object
from cpchain.wallet.fs import get_session, FileInfo, decrypt_file_aes

from cpchain.proxy.client import start_proxy_request, download_proxy_file
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.wallet.simpleqt import event
from cpchain.wallet import events

logger = logging.getLogger(__name__) # pylint: disable=locally-disabled, invalid-name

def update():
    from cpchain.wallet.pages import app
    app.update()


class Broker:
    def __init__(self, wallet):
        self.wallet = wallet
        bin_path = join_with_root(config.chain.contract_bin_path)
        # deploy_contract(bin_path, config.chain.contract_name, default_w3)
        account = get_address_from_public_key_object(self.wallet.market_client.public_key)
        if default_w3:
            account = default_w3.toChecksumAddress(account)
            self.buyer = BuyerAgent(default_w3, bin_path, config.chain.contract_name, account)
            self.seller = SellerAgent(default_w3, bin_path, config.chain.contract_name, account)
            self.handler = Handler(self)
            self.monitor = Monitor(self)

    @defer.inlineCallbacks
    def query_seller_products_order(self, seller):
        # query all order of seller's products, then save it in memory
        orders = yield self.seller.get_all_orders()
        return orders

    def confirm_order(self, order_id_list):
        logger.debug("in buyer confirm order")
        for current_id in order_id_list:
            self.buyer.confirm_order(current_id)
            logger.debug("order %s completed", current_id)

    @defer.inlineCallbacks
    def seller_send_request_stream(self, order_info):
        logger.debug("seller send request to proxy ...")
        order_id = list(order_info.keys())[0]
        new_order_info = order_info[order_id]
        market_hash = new_order_info[0]
        seller_addr = eth_addr_to_string(new_order_info[3])
        buyer_addr = eth_addr_to_string(new_order_info[2])
        buyer_rsa_public_key = new_order_info[1]
        proxy_id = eth_addr_to_string(new_order_info[4])
        session = get_session()
        raw_aes_key = session.query(FileInfo.aes_key) \
            .filter(FileInfo.market_hash == Encoder.bytes_to_base64_str(market_hash)) \
            .all()[0][0]
        logger.debug("start to encrypt aes key with buyer rsa public key")
        logger.debug("raw aes key: %s", raw_aes_key)
        logger.debug("buyer rsa public key: %s", buyer_rsa_public_key)
        encrypted_aes_key = load_der_public_key(buyer_rsa_public_key, backend=default_backend()).encrypt(
            raw_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        logger.debug("encrypted aes key: %s", encrypted_aes_key)
        logger.debug("order info got generated")
        message = Message()
        seller_data = message.seller_data
        message.type = Message.SELLER_DATA
        seller_data.order_id = order_id
        seller_data.order_type = 'stream'
        seller_data.seller_addr = seller_addr
        seller_data.buyer_addr = buyer_addr
        seller_data.market_hash = Encoder.bytes_to_base64_str(market_hash)
        seller_data.AES_key = encrypted_aes_key
        storage = seller_data.storage

        storage_type = session.query(FileInfo.remote_type) \
            .filter(FileInfo.market_hash == Encoder.bytes_to_base64_str(market_hash)) \
            .all()[0][0]
        remote_uri = session.query(FileInfo.remote_uri) \
            .filter(FileInfo.market_hash == Encoder.bytes_to_base64_str(market_hash)) \
            .all()[0][0]
        storage.type = storage_type
        storage.path = remote_uri

        sign_message = SignMessage()
        sign_message.public_key = self.wallet.market_client.public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.create_signature(
            self.wallet.market_client.account.private_key,
            sign_message.data
        )
        try:
            error, AES_key, urls = yield start_proxy_request(sign_message, proxy_id)
            if error:
                logger.error(error)
            else:
                logger.debug(AES_key)
                logger.debug(urls)
                event.emit(events.SELLER_DELIVERY, order_id)
        except Exception as e:
            logger.error(e)

    @defer.inlineCallbacks
    def seller_send_request(self, order_info):
        logger.debug("seller send request to proxy ...")
        order_id = list(order_info.keys())[0]
        new_order_info = order_info[order_id]
        market_hash = new_order_info[0]
        seller_addr = eth_addr_to_string(new_order_info[3])
        buyer_addr = eth_addr_to_string(new_order_info[2])
        buyer_rsa_public_key = new_order_info[1]
        proxy_id = eth_addr_to_string(new_order_info[4])
        session = get_session()
        raw_aes_key = session.query(FileInfo.aes_key) \
            .filter(FileInfo.market_hash == Encoder.bytes_to_base64_str(market_hash)) \
            .all()[0][0]
        logger.debug("start to encrypt aes key with buyer rsa public key")
        logger.debug("raw aes key: %s", raw_aes_key)
        logger.debug("buyer rsa public key: %s", buyer_rsa_public_key)
        encrypted_aes_key = load_der_public_key(buyer_rsa_public_key, backend=default_backend()).encrypt(
            raw_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        logger.debug("encrypted aes key: %s", encrypted_aes_key)
        logger.debug("order info got generated")
        message = Message()
        seller_data = message.seller_data
        message.type = Message.SELLER_DATA
        seller_data.order_id = order_id
        seller_data.order_type = 'file'
        seller_data.seller_addr = seller_addr
        seller_data.buyer_addr = buyer_addr
        seller_data.market_hash = Encoder.bytes_to_base64_str(market_hash)
        seller_data.AES_key = encrypted_aes_key
        storage = seller_data.storage

        storage_type = session.query(FileInfo.remote_type) \
            .filter(FileInfo.market_hash == Encoder.bytes_to_base64_str(market_hash)) \
            .all()[0][0]
        remote_uri = session.query(FileInfo.remote_uri) \
            .filter(FileInfo.market_hash == Encoder.bytes_to_base64_str(market_hash)) \
            .all()[0][0]
        storage.type = storage_type
        storage.path = remote_uri

        sign_message = SignMessage()
        sign_message.public_key = self.wallet.market_client.public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.create_signature(
            self.wallet.market_client.account.private_key,
            sign_message.data
        )
        try:
            error, AES_key, urls = yield start_proxy_request(sign_message, proxy_id)
            if error:
                logger.error(error)
            else:
                logger.debug(AES_key)
                logger.debug(urls)
                event.emit(events.SELLER_DELIVERY, order_id)
        except Exception as e:
            logger.exception(e)


    @defer.inlineCallbacks
    def buyer_send_request(self, order_info):
        logger.debug("buyer send request to proxy ...")
        order_id = list(order_info.keys())[0]
        new_order_info = order_info[order_id]
        seller_addr = eth_addr_to_string(new_order_info[3])
        buyer_addr = eth_addr_to_string(new_order_info[2])
        proxy_id = eth_addr_to_string(new_order_info[4])
        message = Message()
        buyer_data = message.buyer_data
        message.type = Message.BUYER_DATA
        buyer_data.order_id = order_id
        buyer_data.order_type = 'file'
        buyer_data.seller_addr = seller_addr
        buyer_data.buyer_addr = buyer_addr
        buyer_data.market_hash = Encoder.bytes_to_base64_str(new_order_info[0])

        sign_message = SignMessage()
        sign_message.public_key = self.wallet.market_client.public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.create_signature(
            self.wallet.market_client.account.private_key,
            sign_message.data
        )
        error, AES_key, urls = yield start_proxy_request(sign_message, proxy_id)

        def update_buyer_db(file_uri, file_path):
            market_hash = Encoder.bytes_to_base64_str(new_order_info[0])
            file_uuid = file_uri.split('/')[3]
            session = get_session()
            session.query(BuyerFileInfo).filter(BuyerFileInfo.order_id == order_id).update(
                {BuyerFileInfo.market_hash: market_hash, BuyerFileInfo.is_downloaded: True,
                 BuyerFileInfo.file_uuid: file_uuid, BuyerFileInfo.path: file_path,
                 BuyerFileInfo.size: os.path.getsize(file_path)}, synchronize_session=False)
            session.commit()
        if error:
            logger.error(error)
        else:
            file_name = urls[0].split('/')[3]
            file_dir = join_with_rc(config.wallet.download_dir)
            # create if not exists
            os.makedirs(file_dir, exist_ok=True)
            file_path = os.path.join(file_dir, file_name)
            yield download_proxy_file(urls[0], file_path)
            logger.debug("downloaded file path: %s", file_path)
            decrypted_file = decrypt_file_aes(file_path, AES_key)
            logger.debug('Decrypted file path: %s', str(decrypted_file))

            update_buyer_db(urls[0], decrypted_file)
            logger.debug("file has been downloaded")
            logger.debug("put order into confirmed queue, order id: %s", order_id)
        event.emit(events.BUYER_RECEIVE, order_id)

    @defer.inlineCallbacks
    def buyer_send_request_stream(self, order_info):
        logger.debug("buyer send request to proxy ...")
        order_id = list(order_info.keys())[0]
        new_order_info = order_info[order_id]
        seller_addr = eth_addr_to_string(new_order_info[3])
        buyer_addr = eth_addr_to_string(new_order_info[2])
        proxy_id = eth_addr_to_string(new_order_info[4])
        message = Message()
        buyer_data = message.buyer_data
        message.type = Message.BUYER_DATA
        buyer_data.order_id = order_id
        buyer_data.order_type = 'stream'
        buyer_data.seller_addr = seller_addr
        buyer_data.buyer_addr = buyer_addr
        buyer_data.market_hash = Encoder.bytes_to_base64_str(new_order_info[0])

        sign_message = SignMessage()
        sign_message.public_key = self.wallet.market_client.public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.create_signature(
            self.wallet.market_client.account.private_key,
            sign_message.data
        )

        error, AES_key, urls = yield start_proxy_request(sign_message, proxy_id)

        def update_buyer_db(stream_id):
            session = get_session()
            session.query(BuyerFileInfo).filter(BuyerFileInfo.order_id == order_id).update(
                {
                    BuyerFileInfo.is_downloaded: True,
                    BuyerFileInfo.path: stream_id,
                }, synchronize_session=False)
            session.commit()
        if error:
            logger.error(error)
        else:
            update_buyer_db(json.dumps(urls))
            logger.debug("Stream data has been geted")
        event.emit(events.BUYER_RECEIVE, order_id)


class Monitor:
    def __init__(self, broker):
        self.broker = broker
        start_id = self.broker.seller.get_order_num()
        self.chain_monitor = OrderMonitor(start_id, self.broker.seller)

class Handler:
    def __init__(self, broker):
        self.broker = broker


    def buy_product(self, msg_hash, file_title, proxy, seller, value):
        logger.debug("start to buy product")
        seller_addr = get_address_from_public_key_object(seller)
        desc_hash = Encoder.str_to_base64_byte(msg_hash)
        rsa_key = RSACipher.load_public_key()
        # rsa_key = self.broker.wallet.market_client.public_key
        logger.debug("desc hash: %s", desc_hash)
        logger.info('Value: %s', value)
        product = OrderInfo(
            desc_hash=desc_hash,
            buyer_rsa_pubkey=rsa_key,
            seller=self.broker.buyer.web3.toChecksumAddress(seller_addr),
            proxy=self.broker.buyer.web3.toChecksumAddress(proxy),
            secondary_proxy=self.broker.buyer.web3.toChecksumAddress(proxy),
            proxy_value=10,
            value=value,
            time_allowed=3600 * 24
        )
        logger.debug("product info has been created")
        logger.debug("product info: %s", product)
        logger.debug("seller address: %s", product.seller)
        d_placed_order = deferToThread(self.broker.buyer.place_order, product)

        def add_bought_order(order_id):
            logger.debug("start to update local database")
            new_buyer_file_info = BuyerFileInfo(order_id=order_id,
                                                market_hash=Encoder.bytes_to_base64_str(desc_hash),
                                                file_title=file_title, is_downloaded=False)
            add_file(new_buyer_file_info)
            logger.debug("update local db completed")
            event.emit(events.PAY, (order_id, msg_hash))
            # Update the purchased downloaded tab in the main window of wallet
        d_placed_order.addCallback(add_bought_order)
