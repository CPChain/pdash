from cpchain.proxy.server import ProxyServer
from cpchain.proxy.file_server import FileServer
from cpchain.proxy.kadnet import KadNode
from cpchain.proxy.stream_ws import WSServer
from cpchain.proxy.stream_restful import RestfulServer

from cpchain.proxy.account import set_proxy_account

class Node:
    def __init__(self, account_id=0):
        set_proxy_account(account_id)

        self.proxy_server = ProxyServer()
        self.file_server = FileServer()
        self.stream_ws_server = WSServer()
        self.stream_restful_server = RestfulServer()

        self.kad_node = KadNode()

    def run(self):
        self.proxy_server.run()
        self.file_server.run()
        self.stream_ws_server.run()
        self.stream_restful_server.run()

        self.kad_node.run()

    def stop(self):
        self.proxy_server.stop()
        self.file_server.stop()
        self.stream_ws_server.stop()
        self.stream_restful_server.stop()

        self.kad_node.stop()
