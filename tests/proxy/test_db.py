import unittest

from cpchain.proxy.db import Trade, ProxyDB

class DBTest(unittest.TestCase):
    def test_proxy_db(self):
        db = ProxyDB('sqlite:///:memory:')

        trade = Trade()
        trade.order_id = 1
        trade.order_type = 'file'
        trade.buyer_addr = 'buyer_addr'
        trade.seller_addr = 'seller_addr'
        trade.market_hash = 'market_hash'
        trade.AES_key = b'AES_key'
        trade.data_path = 'data_path'
        trade.order_delivered = False

        db.insert(trade)

        result = db.query(trade)
        self.assertEqual(result.AES_key, b'AES_key')

        db.delete(result)

        result = db.query(trade)
        self.assertEqual(result, None)
