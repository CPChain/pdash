# pylint: disable=wrong-import-position
import sys
import logging

import asyncio

from twisted.internet import asyncioreactor
loop = asyncio.get_event_loop()
asyncioreactor.install(eventloop=loop)

from twisted.internet import reactor
from twisted.python import log

from cpchain.proxy.node import Peer

logger = logging.getLogger(__name__)

if len(sys.argv) != 3:
    logger.info("Usage: python3 start_proxy.py <tracker ip:port> <dht ip:port>")
    logger.info("example: python3 start_proxy.py 127.0.0.1:8101 127.0.0.1:8201")
    sys.exit(1)

log.startLogging(sys.stdout)

(addr, port) = sys.argv[1].split(':')
boot_node = (str(addr), int(port))

peer = Peer()
peer.start_service()
peer.join_centra_net(
    boot_node=boot_node
    )

(addr, port) = sys.argv[2].split(':')
boot_nodes = [(str(addr), int(port))]

boot_nodes = [('127.0.0.1', 8201)]
peer.join_decentra_net(
    boot_nodes=boot_nodes
    )

reactor.run()
