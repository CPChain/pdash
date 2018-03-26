

# monitor changes on the chain and get new orders of seller
class OrderMonitor:

    def __init__(self, start_id, seller_trans):
        self.start_id = start_id
        self.trans = seller_trans

    # returns a list of new orders generated since last update
    def get_new_order(self, account=None):
        account = account or self.trans.web3.eth.defaultAccount
        end_id = self.trans.get_order_num()
        new_orders = self.trans.filter_seller_range(self.start_id, end_id, account)
        self.update_start_id(end_id)
        return new_orders

    def update_start_id(self, new_start_id):
        self.start_id = new_start_id



