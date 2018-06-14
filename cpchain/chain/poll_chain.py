

# monitor changes on the chain and get new orders of seller
class OrderMonitor:

    def __init__(self, start_id, seller_agent):
        self.start_id = start_id
        self.agent = seller_agent

    # returns a list of new orders generated since last update
    def get_new_order(self,):
        end_id = self.agent.get_order_num()
        new_orders = self.agent.filter_seller_range(self.start_id, end_id,)
        self.update_start_id(end_id)
        return new_orders

    def update_start_id(self, new_start_id):
        self.start_id = new_start_id

