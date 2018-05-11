from cpchain import config
from cpchain.chain import models
from cpchain.utils import logging
from cpchain.chain import utils

from .wait_utils import wait_for_transaction_receipt


# base transaction class for interacting with cpchain
class Agent:
    ONE_ETH_IN_WEI = 10**18  # 1 ETH == 1,000,000,000,000,000,000 Wei

    # NB contract object belongs to web3, and so does account.
    # we shouldn't pass params like this.)
    def __init__(self, web3, bin_path, contract_name):
        self.web3 = web3
        contract_interface = utils.read_contract_interface(bin_path, contract_name)
        self.contract = web3.eth.contract(address=utils.read_contract_address(contract_name),
                                          abi=contract_interface['abi'],
                                          bytecode=contract_interface['bin'])

    def query_order(self, order_id) -> models.OrderInfo:
        order_record = self.contract.call().orderRecords(order_id)
        logging.debug("Order record NO.{:d}: {record}\n".format(order_id, record=order_record))
        return order_record

    def get_order_num(self) -> "number of orders":
        order_num = self.contract.call().numOrders()
        logging.debug("Total number of orders: {:d}\n".format(order_num))
        return order_num


class BuyerAgent(Agent):

    # order_info is a dictionary that contains parameters for an order
    def place_order(self, order_info: models.OrderInfo, account=None) -> "order id":
        account = account or self.web3.eth.defaultAccount
        event_filter = self.contract.eventFilter('OrderInitiated', {'filter': {'from': account}})
        # Initiate an order
        offered_price = self.ONE_ETH_IN_WEI * order_info.value
        transaction = {
            'value': offered_price,
            'from': account
        }
        tx_hash = self.contract.functions.placeOrder(
            order_info.desc_hash,
            order_info.buyer_rsa_pubkey,
            order_info.seller,
            order_info.proxy,
            order_info.secondary_proxy,
            order_info.proxy_value,
            order_info.time_allowed
        ).transact(transaction)
        logging.debug("Thank you for using CPChain! Initiated Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        # Get order id through emitted event
        order_event_list = event_filter.get_new_entries()
        if len(order_event_list) == 0:
            order_id = -1
        else:
            order_id = order_event_list[0]['args']['orderId']
        logging.debug("TransactionID: {:d}".format(order_id))
        return order_id

    def withdraw_order(self, order_id, account=None):
        account = account or self.web3.eth.defaultAccount
        transaction = {'value': 0, 'from': account}
        tx_hash = self.contract.transact(transaction).buyerWithdraw(order_id)
        logging.debug("Thank you for your using! Order is withdrawn, Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def confirm_order(self, order_id, account=None):
        account = account or self.web3.eth.defaultAccount
        transaction = {'value': 0, 'from': account}
        tx_hash = self.contract.transact(transaction).confirmDeliver(order_id)
        logging.debug("Thank you for confirming deliver! Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def dispute(self, order_id, account=None):
        account = account or self.web3.eth.defaultAccount
        transaction = {'value': 0, 'from': account}
        tx_hash = self.contract.transact(transaction).buyerDispute(order_id)
        logging.debug("You have started a dispute! Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash


class SellerAgent(Agent):
    def claim_timeout(self, order_id, account=None):
        account = account or self.web3.eth.defaultAccount
        transaction = {'value': 0, 'from': account}
        tx_hash = self.contract.transact(transaction).sellerClaimTimedOut(order_id)
        logging.debug("Your money is claimed because of time out! Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def filter_seller_range(self, start_id, end_id, account=None):
        account = account or self.web3.eth.defaultAccount
        id_list = []
        for current_id in range(start_id, end_id):
            current_seller = self.query_order(current_id)[2]
            if current_seller == account:
                id_list.append(current_id)
        return id_list

    
class ProxyAgent(Agent):
    
    def claim_relay(self, order_id, relay_hash, account=None):
        account = account or self.web3.eth.defaultAccount
        transaction = {'value': 0, 'from': account}
        tx_hash = self.contract.transact(transaction).deliverMsg(relay_hash, order_id)
        logging.debug("You have registered relay of file on CPChain! Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def handle_dispute(self, order_id, result, account=None):
        account = account or self.web3.eth.defaultAccount
        transaction = {'value': 0, 'from': account}
        tx_hash = self.contract.transact(transaction).proxyJudge(order_id, result)
        logging.debug("You have submit the result for dispute on CPChain! Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash
