import signal
import sys
import time

from cpchain.utils import reactor

from PyQt5.QtWidgets import QApplication
# # do it before any other twisted code.
# app = None
# def install_reactor():
#     global app
#     app = QApplication(sys.argv)
#     import qt5reactor; qt5reactor.install()
# install_reactor()

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

# from cpchain.wallet.ui import MainWindow
from cpchain.wallet.chain import Broker
from cpchain.wallet.net import MarketClient
from cpchain.wallet import fs
from cpchain.crypto import RSACipher, Encoder
from cpchain.account import Accounts

import logging
logger = logging.getLogger(__name__)


class Wallet:
    def __init__(self, reactor):
        self.reactor = reactor
        self.accounts = Accounts()
        # self.main_wnd = MainWindow(self)
        self.chain_broker = Broker(self)
        self.market_client = MarketClient(self)


        # self._initialize_system()


    def _initialize_system(self):
        # TODO logging setup
        pass

        # def monitor_chain_event():
        #     seller_poll_chain = LoopingCall(seller_chain_client.send_request)
        #     seller_poll_chain.start(10)
        #     buyer_check_confirm = LoopingCall(buyer_chain_client.check_confirm)
        #     buyer_check_confirm.start(15)
        # monitor_chain_event()


def main():
        wallet = Wallet(reactor)
        wallet.market_client.query_product('Medicine')
        print('end')
        # file_info = fs.get_file_list()[0]
        # hashcode = file_info.hashcode
        # path = file_info.path
        # size = file_info.size
        # product_id = file_info.id
        # remote_type = file_info.remote_type
        # remote_uri = file_info.remote_uri
        # name = file_info.name
        # logger.debug('encrypt aes key')
        # encrypted_key = RSACipher.encrypt(file_info.aes_key)
        # encrypted_key = Encoder.bytes_to_base64_str(encrypted_key)
        # wallet.market_client.upload_file_info(hashcode, path, size, product_id, remote_type, remote_uri,
        #                                           encrypted_key, name)
        # pinfo = fs.get_file_list()[0]
        # logger.debug("product id: %s", pinfo.id)
        # wallet.market_client.publish_product(pinfo.id, 'title', 'description', 123,
        #                                      'tag', '2018-04-01 10:10:10',
        #                                      '2018-04-01 10:10:10', '123456')

        # d.addBoth(default_callback())
        # sys.exit(reactor.run())


if __name__ == '__main__':
    main()
