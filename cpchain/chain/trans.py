from populus.utils.wait import wait_for_transaction_receipt

from cpchain import config
from cpchain.chain import models


# Base transaction class for interacting with CPChain
class Trans:
    ONE_ETH_IN_WEI = 10**18  # 1 ETH == 1,000,000,000,000,000,000 Wei

    def __init__(self, web3, contract, account):
        self.contract = contract
        self.web3 = web3
        self.web3.eth.defaultAccount = account

    def query_order(self, order_id) -> models.OrderInfo:
        order_record = self.contract.call().orderRecords(order_id)
        print("Order record NO.{:d}: {record}\n".format(order_id, record=order_record))
        return order_record


class BuyerTrans(Trans):

    def __init__(self, web3, contract, account):
        super().__init__(web3, contract, account)

    # order_info is a dictionary that contains parameters for an order
    def place_order(self, order_info: models.OrderInfo) -> "order id":
        transfer_filter = self.contract.on('OrderInitiated', {'filter': {'from': self.web3.eth.defaultAccount}})
        # Initiate a transaction
        offered_price = self.ONE_ETH_IN_WEI * order_info.value
        transaction = {
            'value': offered_price,
            'from': self.web3.eth.defaultAccount,
            'to': self.contract.address
        }
        tx_hash = self.contract.transact(transaction).placeOrder(
            order_info.desc_hash,
            order_info.seller,
            order_info.proxy,
            order_info.secondary_proxy,
            order_info.proxy_value
        )
        print("Thank you for using CPChain! Initiated Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash, timeout=180)
        # Get transaction through emitted event
        order_id = transfer_filter.get()[0]['args']['orderId']
        print("TransactionID: {:d}".format(order_id))
        return order_id

    def withdraw_order(self, order_id):
        transaction = {'value': 0, 'from': self.web3.eth.defaultAccount}
        tx_hash = self.contract.transact(transaction).buyerWithdraw(order_id)
        print("Thank you for your using! Order is withdrawn, Tx hash {tx}".format(tx=tx_hash))
        return tx_hash

    def confirm_order(self, order_id):
        transaction = {'value': 0, 'from': self.web3.eth.defaultAccount}
        tx_hash = self.contract.transact(transaction).confirmDeliver(order_id)
        print("Thank you for confirming deliver! Tx hash {tx}".format(tx=tx_hash))
        return tx_hash

    def dispute(self, order_id):
        transaction = {'value': 0, 'from': self.web3.eth.defaultAccount}
        tx_hash = self.contract.transact(transaction).buyerDispute(order_id)
        print("You have started a dispute! Tx hash {tx}".format(tx=tx_hash))
        return tx_hash


class SellerTrans(Trans):
    def __init__(self, web3, contract, account):
        super().__init__(web3, contract, account)

    def claim_timeout(self, order_id):
        transaction = {'value': 0, 'from': self.web3.eth.defaultAccount}
        tx_hash = self.contract.transact(transaction).sellerClaimTimedOut(order_id)
        print("Your money is claimed because of time out! Tx hash {tx}".format(tx=tx_hash))
        return tx_hash

    
class ProxyTrans(Trans):
    def __init__(self, web3, contract, account):
        super().__init__(web3, contract, account)

    def claim_relay(self, order_id, relay_hash):
        transaction = {'value': 0, 'from': self.web3.eth.defaultAccount}
        tx_hash = self.contract.transact(transaction).deliverMsg(relay_hash, order_id)
        print("You have registered relay of file on CPChain! Tx hash {tx}".format(tx=tx_hash))
        return tx_hash

    def handle_dispute(self, order_id, result):
        transaction = {'value': 0, 'from': self.web3.eth.defaultAccount}
        tx_hash = self.contract.transact(transaction).proxyJudge(order_id, result)
        print("You have submit the result for dispute on CPChain! Tx hash {tx}".format(tx=tx_hash))
        return tx_hash


def create_trans(cls, web3, contract, account):
    return cls(web3, contract, account)
