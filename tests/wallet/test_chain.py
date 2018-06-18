from twisted.logger import globalLogBeginner, textFileLogObserver
import sys
globalLogBeginner.beginLoggingTo([textFileLogObserver(sys.stdout)])

from cpchain.wallet.wallet import Wallet
from cpchain.wallet.chain import Handler, Monitor, Broker
from twisted.internet import reactor
from cpchain.chain.utils import deploy_contract, default_w3, join_with_root
from cpchain.utils import config
from twisted.internet.task import LoopingCall

from cpchain.proxy.node import pick_proxy, start_proxy_request
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage

import logging

logger = logging.getLogger(__name__)

wallet = Wallet(reactor)
broker = Broker(wallet)
handler = Handler(broker)
monitor = Monitor(broker)


def test_deploy_contract():
    w3 = default_w3
    bin_path = join_with_root(config.chain.contract_bin_path)
    new_contract_name = config.chain.contract_name
    deploy_contract(bin_path, new_contract_name, w3)
    return new_contract_name


def test_buy_product():
    logger.debug("start to buy product ...")
    msg_hash = "+DgQ/xzcIwKf3ZciqWST+n57CRrZRDBCcMjO7Yhk0KE="
    file_title = "testFileTitle"
    handler.buy_product(msg_hash, file_title)


def test_monitor_new_order():
    logger.debug("monitor new order ...")
    monitor.monitor_new_order()


def test_handle_new_order():
    logger.debug("start to handle new orders ...")
    handler.handle_new_order()


def test_pick_proxy():
    d = pick_proxy()
    d.addCallback(lambda proxy_addr: print(proxy_addr))


def test_init():
    monitor_new_order = LoopingCall(test_monitor_new_order)
    monitor_new_order.start(5)

    buy_product = LoopingCall(test_buy_product)
    buy_product.start(20)

    handle_new_order = LoopingCall(test_handle_new_order)
    handle_new_order.start(60)


def main():
    logging.debug("start")
    test_init()
    reactor.run()


if __name__ == '__main__':
    test_pick_proxy()
    reactor.run()
    # main()
    # test_deploy_contract()
    # print("test")