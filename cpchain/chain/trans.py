from populus.utils.wait import wait_for_transaction_receipt

from cpchain import config     
from cpchain.chain import models
from cpchain.utils import logging
from cpchain.chain import utils


# base transaction class for interacting with cpchain
class Trans:
    ONE_ETH_IN_WEI = 10**18  # 1 ETH == 1,000,000,000,000,000,000 Wei

    # NB contract object belongs to web3, and so does account.
    # we shouldn't pass params like this.
    def __init__(self, web3, contract_name):
        self.web3 = web3
        contract_interface = utils.read_contract_interface(contract_name)
        self.contract = web3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
        self.contract.address = utils.read_contract_address(contract_name)

    def query_order(self, order_id) -> models.OrderInfo:
        order_record = self.contract.call().orderRecords(order_id)
        logging.debug("Order record NO.{:d}: {record}\n".format(order_id, record=order_record))
        return order_record


class BuyerTrans(Trans):

    # order_info is a dictionary that contains parameters for an order
    def place_order(self, order_info: models.OrderInfo, account=None) -> "order id":
        account = account or self.web3.eth.defaultAccount
        event_filter = self.contract.on('OrderInitiated', {'filter': {'from': account}})
        # Initiate an order
        offered_price = self.ONE_ETH_IN_WEI * order_info.value
        transaction = {
            'value': offered_price,
            'from': account
        }
        tx_hash = self.contract.transact(transaction).placeOrder(
            order_info.desc_hash,
            order_info.seller,
            order_info.proxy,
            order_info.secondary_proxy,
            order_info.proxy_value,
            order_info.time_allowed
        )
        logging.debug("Thank you for using CPChain! Initiated Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        # Get order id through emitted event
        order_id = event_filter.get()[0]['args']['orderId']
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


class SellerTrans(Trans):
    def claim_timeout(self, order_id, account=None):
        account = account or self.web3.eth.defaultAccount
        transaction = {'value': 0, 'from': account}
        tx_hash = self.contract.transact(transaction).sellerClaimTimedOut(order_id)
        logging.debug("Your money is claimed because of time out! Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    
class ProxyTrans(Trans):
    
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
