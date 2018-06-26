import sys

from twisted.internet import reactor

from cpchain.utils import reactor

from cpchain.wallet.chain import Broker
from cpchain.wallet.net import MarketClient

from cpchain.account import Accounts

import logging
logger = logging.getLogger(__name__)

class Wallet:
    def __init__(self, reactor):
        self.reactor = reactor
        self.accounts = Accounts()
        # self.main_wnd = MainWindow(self)
        self.market_client = MarketClient(self)
        self.chain_broker = Broker(self)


    def _initialize_system(self):
        # TODO logging setup
        pass

        # def monitor_chain_event():
        #     seller_poll_chain = LoopingCall(seller_chain_client.send_request)
        #     seller_poll_chain.start(10)
        #     buyer_check_confirm = LoopingCall(buyer_chain_client.check_confirm)
        #     buyer_check_confirm.start(15)
        # monitor_chain_event()

    def set_main_wnd(self, main_wnd):
        self.main_wnd = main_wnd


def main():
        sys.exit(reactor.run())


if __name__ == '__main__':
    main()
