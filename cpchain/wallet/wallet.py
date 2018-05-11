import signal
import sys

from PyQt5.QtWidgets import QApplication
# do it before any other twisted code.
app = None
def install_reactor():
    global app
    app = QApplication(sys.argv)
    import qt5reactor; qt5reactor.install()
install_reactor()

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

# from cpchain.wallet.ui import MainWindow
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
        # self.chain_broker = Broker(self)
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

    # for test
    # mc = MarketClient(wallet)
    # logger.debug('init mc')
    # mc.query_carousel()
    # mc.query_hot_tag()
    # mc.query_promotion()
    # test end

    sys.exit(reactor.run())


if __name__ == '__main__':
    main()


