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
        self.market_client = MarketClient(self)
        self.chain_broker = Broker(self)

    def _initialize_system(self):
        pass

    def set_main_wnd(self, main_wnd):
        self.main_wnd = main_wnd


def main():
        sys.exit(reactor.run())



if __name__ == '__main__':
    main()
