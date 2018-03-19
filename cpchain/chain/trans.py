class Trans:
    def __init__(self, chain, contract):
        self.chain = chain
        self.contract = contract

    def _deploy_contract():
        pass


class BuyerTrans(Trans):
    def place_order(item_order) -> "order id":
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
