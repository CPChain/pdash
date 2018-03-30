from twisted.internet.protocol import ServerFactory, ClientFactory
from twisted.protocols.basic import NetstringReceiver
from twisted.internet import defer, reactor

from treq.client import HTTPClient

from cpchain.utils import logging


class SellerClient(NetstringReceiver):
    def connectionMade(self):
        logging.info("connnected to master.")

        # add a message 
        status = zebra_pb2.Status()
        status.event_type = status.REGISTER

        self.sendString(status.SerializeToString())


    def connectionLost(self, reason):
        logging.info("slave connection lost.")


    def stringReceived(self, string):
        status = zebra_pb2.Status()
        status.ParseFromString(string)
    
        if status.event_type is status.LAUNCH:
            self.launch_flow(status)
            return 

        if status.event_type is status.RATELIMIT:
            self.rate_limit_flow(status)
            return

        logging.error("wrong event type.")

        
class SellerClientFactory(ClientFactory):
    protocol = SellerClient
    # keep connecting.
    def clientConnectionFailed(self, connector, reason):
        connector.connect()



class MarketClient:
    def __init__(self):
        self.client = HTTPClient(reactor)







# we shall also add buyer client.
