class Trans:
    def __init__(self, web3=None, contract_name=""):
        pass

class BuyerTrans(Trans):
    def place_order(order_info) -> "order id":
        pass

    def withdraw_order(order_id):
        pass

    def confirm_order(order_id):
        pass

    def dispute(order_id):
        pass


class SellerTrans(Trans):
    def claim_timeout():
        pass

    
class ProxyTrans(Trans):
    def claim_relay():
        pass

    def handle_dispute():
        pass
