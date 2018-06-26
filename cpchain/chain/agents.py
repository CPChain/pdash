import logging

from cpchain import config
from cpchain.chain import models
from cpchain.chain import utils

from .wait_utils import wait_for_transaction_receipt

logger = logging.getLogger(__name__)


# base transaction class for interacting with cpchain
class Agent:
    ONE_ETH_IN_WEI = 10**18  # 1 ETH == 1,000,000,000,000,000,000 Wei

    def __init__(self, web3, bin_path, contract_name, account=None):
        self.web3 = web3
        contract_interface = utils.read_contract_interface(bin_path, contract_name)
        self.contract = web3.eth.contract(address=utils.read_contract_address(contract_name),
                                          abi=contract_interface['abi'],
                                          bytecode=contract_interface['evm']['bytecode']['object'])
        if account:
            account = self.web3.toChecksumAddress(account)
        self.account = account or self.web3.eth.defaultAccount

    def query_order(self, order_id) -> models.OrderInfo:
        order_record = self.contract.call().orderRecords(order_id)
        logger.debug("Order record NO.{:d}: {record}\n".format(order_id, record=order_record))
        return order_record

    def get_order_num(self) -> "number of orders":
        order_num = self.contract.call().numOrders()
        logger.debug("Total number of orders: {:d}\n".format(order_num))
        return order_num

    def query_dispute(self, dispute_id):
        dispute_record = self.contract.call().disputeRecords(dispute_id)
        logger.debug("Dispute record NO.{:d}: {record}\n".format(dispute_id, record=dispute_record))
        return dispute_record

    def fetch_dispute_result(self, order_id):
        order = self.query_order(order_id)
        dispute_id = order[11]
        dispute = self.query_dispute(dispute_id)
        return dispute


class BuyerAgent(Agent):

    # order_info is a dictionary that contains parameters for an order
    def place_order(self, order_info: models.OrderInfo,) -> "order id":
        logger.debug("in place order")
        event_filter = self.contract.eventFilter('OrderInitiated', {'filter': {'from': self.account}})
        # Initiate an order
        logger.debug("initiate an order")
        offered_price = self.ONE_ETH_IN_WEI * order_info.value
        transaction = {
            'value': offered_price,
            'from': self.account,
        }
        logger.debug("contract address: %s", self.contract.address)
        logger.debug("estimate gas")
        gas_estimate = self.contract.functions.placeOrder(
            order_info.desc_hash,
            order_info.buyer_rsa_pubkey,
            order_info.seller,
            order_info.proxy,
            order_info.secondary_proxy,
            order_info.proxy_value,
            order_info.time_allowed
        ).estimateGas(transaction)
        transaction['gas'] = gas_estimate + 100000
        logger.debug("issue transaction ...")
        tx_hash = self.contract.functions.placeOrder(
            order_info.desc_hash,
            order_info.buyer_rsa_pubkey,
            order_info.seller,
            order_info.proxy,
            order_info.secondary_proxy,
            order_info.proxy_value,
            order_info.time_allowed
        ).transact(transaction)

        logger.debug("Thank you for using CPChain! Initiated Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        # Get order id through emitted event
        order_event_list = event_filter.get_new_entries()
        if len(order_event_list) == 0:
            order_id = -1
        else:
            order_id = order_event_list[0]['args']['orderId']
        logger.debug("TransactionID: {:d}".format(order_id))
        return order_id

    def withdraw_order(self, order_id,):
        transaction = {'value': 0, 'from': self.account,}
        tx_hash = self.contract.functions.buyerWithdraw(order_id).transact(transaction)
        logger.debug("Thank you for your using! Order is withdrawn, Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def confirm_order(self, order_id,):
        transaction = {'value': 0, 'from': self.account,}
        tx_hash = self.contract.functions.buyerConfirmDeliver(order_id).transact(transaction)
        logger.debug("Thank you for confirming deliver! Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def dispute(self, order_id,):
        transaction = {'value': 0, 'from': self.account,}
        tx_hash = self.contract.functions.buyerDispute(order_id).transact(transaction)
        logger.debug("You have started a dispute! Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def check_proxy_is_ready(self, order_id,):
        order = self.query_order(order_id)
        return order[10] == 2 # order.state == ProxyFetched

    def confirm_dispute(self, order_id, if_agree,):
        transaction = {'value': 0, 'from': self.account,}
        tx_hash = self.contract.functions.buyerAgreeOrNot(order_id, if_agree).transact(transaction)
        logger.debug("You are {} agree with the dispute result".format(if_agree))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def rate_proxy(self, order_id, rate,):
        transaction = {'value': 0, 'from': self.account,}
        tx_hash = self.contract.functions.buyerRateProxy(order_id, rate).transact(transaction)
        logger.debug("You rated the proxy with {}".format(rate))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash


class SellerAgent(Agent):
    def claim_timeout(self, order_id,):
        transaction = {'value': 0, 'from': self.account,}
        tx_hash = self.contract.functions.sellerClaimTimeOut(order_id).transact(transaction)
        logger.debug("Your money is claimed because of time out! Tx hash {tx}".format(tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def filter_seller_range(self, start_id, end_id,):
        id_list = []
        for current_id in range(start_id+1, end_id+1):
            current_seller = self.query_order(current_id)[2]
            if current_seller == self.account:
                id_list.append(current_id)
        return id_list

    def confirm_order(self, order_id,):
        logger.debug("in seller confirm order, order id: %s", order_id)
        logger.debug("seller address: %s", self.account)
        offered_price = self.query_order(order_id)[6]
        if offered_price < 0:
            return None
        transaction = {'value': offered_price, 'from': self.account,}
        logger.debug("transaction: %s", transaction)
        tx_hash = self.contract.functions.sellerConfirm(order_id).transact(transaction)
        logger.debug("You have confirmed the order:{order_id} and deposited {value} to contract {address}".format(order_id=order_id, value=offered_price, address=self.contract.address))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def confirm_dispute(self, order_id, if_agree,):
        transaction = {'value': 0, 'from': self.account,}
        gas_estimate = self.contract.functions.sellerAgreeOrNot(order_id, if_agree).estimateGas(transaction)
        transaction['gas'] = gas_estimate + 10000
        tx_hash = self.contract.functions.sellerAgreeOrNot(order_id, if_agree).transact(transaction)
        logger.debug("You are {} agree with the dispute result".format(if_agree))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def rate_proxy(self, order_id, rate,):
        transaction = {'value': 0, 'from': self.account,}
        tx_hash = self.contract.functions.sellerRateProxy(order_id, rate).transact(transaction)
        logger.debug("You rated the proxy with {}".format(rate))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash


class ProxyAgent(Agent):

    def deposit(self, value,):
        if value < 0:
            return None
        transaction = {'value': value, 'from': self.account,}
        tx_hash = self.contract.functions.proxyDeposit().transact(transaction)
        logger.debug("You have deposited {value} to contract {address}! Tx hash {tx}".format(value=value, address=self.contract.address, tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def query_deposit(self,):
        deposit = self.contract.call().proxyDeposits(self.account)
        return deposit

    def withdraw(self, value,):
        if value > self.query_deposit():
            return None
        transaction = {'value': 0, 'from': self.account,}
        tx_hash = self.contract.functions.proxyWithdraw(value).transact(transaction)
        logger.debug("You have withdrawn {value} from contract {address}! Tx hash {tx}".format(value=value, address=self.contract.address, tx=tx_hash))
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def check_order_is_ready(self, order_id,):
        order_state = self.query_order(order_id)[10]
        return order_state == 1

    def claim_fetched(self, order_id,):
        transaction = {'value': 0, 'from': self.account,}
        gas_estimate = self.contract.functions.proxyFetched(order_id).estimateGas(transaction)
        transaction['gas'] = gas_estimate + 10000
        tx_hash = self.contract.functions.proxyFetched(order_id).transact(transaction)
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def claim_delivered(self, order_id, relay_hash, ):
        transaction = {'value': 0, 'from': self.account,}
        tx_hash = self.contract.functions.proxyDelivered(relay_hash, order_id).transact(transaction)
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash

    def handle_dispute(self, order_id, result,):
        transaction = {'value': 0, 'from': self.account,}
        tx_hash = self.contract.functions.proxyProcessDispute(order_id, result).transact(transaction)
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash


class TrentAgent(Agent):

    def fetch_unhandled_disputes(self, start_id, end_id, ) -> "list of order_id":
        disputed_order_ids= []
        for id in range(start_id, end_id):
            order_state = self.query_order(id)[10]
            if order_state == 8: # order.state == Disputed
                dispute_record = self.fetch_dispute_result(id)
                if dispute_record[7] == 1 and (not (dispute_record[4] and dispute_record[5])):
                    disputed_order_ids.append(id)
        return disputed_order_ids

    def handle_dispute(self, order_id, badBuyer, badSeller, badProxy, ):
        transaction = {'value': 0, 'from': self.account,}
        gas_estimate = self.contract.functions.trentHandleDispute(order_id, badBuyer, badSeller, badProxy).estimateGas(transaction)
        transaction['gas'] = gas_estimate + 10000
        tx_hash = self.contract.functions.trentHandleDispute(order_id, badBuyer, badSeller, badProxy).transact(transaction)
        wait_for_transaction_receipt(self.web3, tx_hash)
        return tx_hash
