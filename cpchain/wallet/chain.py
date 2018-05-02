from cpchain.crypto import Encoder, RSACipher
from cpchain.chain.models import OrderInfo
from twisted.internet.threads import deferToThread
from cpchain.utils import config
from cpchain.chain.trans import BuyerTrans, SellerTrans
from cpchain.chain.utils import default_web3
from cpchain.wallet.db import BuyerFileInfo
from cpchain.wallet.fs import add_file
import queue


class Broker:
    def __init__(self, wallet):
        self.wallet = wallet

        self.buyer = BuyerTrans(default_web3, config.chain.core_contract)
        self.seller = SellerTrans(default_web3, config.chain.core_contract)

        # buyer_chain_client = BuyerChainClient(main_wnd, market_client)
        # seller_chain_client = SellerChainClient(main_wnd, market_client)


class BuyerClient:
    def __init__(self, broker):
        self.broker = broker
        self.order_id_list = queue.Queue()


    def buy_product(self, msg_hash, file_title):
        desc_hash = Encoder.str_to_base64_byte(msg_hash)
        rsa_key = RSACipher.load_public_key()
        product = OrderInfo(
            desc_hash=desc_hash,
            buyer_rsa_pubkey=rsa_key,
            seller=self.broker.buyer.web3.eth.defaultAccount,
            proxy=self.broker.buyer.web3.eth.defaultAccount,
            secondary_proxy=self.broker.buyer.web3.eth.defaultAccount,
            proxy_value=10,
            value=20,
            time_allowed=1000
        )
        placed_order_id = deferToThread(self.broker.buyer.place_order, product)

        def handle_new_order(order_id):
            self.order_id_list.put(order_id)
            print("Before new buyer file info. ")
            new_buyer_file_info = BuyerFileInfo(order_id=order_id, market_hash=Encoder.bytes_to_base64_str(desc_hash),
                                                file_title=file_title, is_downloaded=False)
            add_file(new_buyer_file_info)
            self.update_treasure_pane()
            print('In place order callback order id: ', self.order_id_list)
        placed_order_id.addCallback(handle_new_order)

        return self.order_id_list

    def update_treasure_pane(self):
        pass

    def check_confirm(self):
        if not self.order_id_list.empty():
            current_id = self.order_id_list.get()
            order_info = deferToThread(self.broker.buyer.query_order(current_id))
            # If state is Delivered, request to proxy
        else:
            print('no placed order')

        def check_state(order_info):
            state = order_info[10]
            if state == 1:
                self.send_request(current_id)

        order_info.addCallback(check_state)

    def send_request(self, order_id):
        pass



class SellerClient:
    def __init__(self, broker):
        self.broker = broker

