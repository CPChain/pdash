import sys
from twisted.python import log

# TODO: to be removed, for testing purpose only
from cpchain.proxy import chain
chain.order_is_ready_on_chain = lambda _: True
chain.claim_data_fetched_to_chain = lambda _: True
chain.claim_data_delivered_to_chain = lambda _: True

from cpchain.utils import reactor
from cpchain.proxy.node import Node


log.startLogging(sys.stdout)

proxy_node = Node()
proxy_node.run()

try:
    reactor.run()
except KeyboardInterrupt:
    pass
finally:
    proxy_node.stop()
