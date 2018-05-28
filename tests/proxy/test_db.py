import unittest

from cpchain.proxy.db import Trade, ProxyDB

class DBTest(unittest.TestCase):
    def test_proxy_db(self):
        db = ProxyDB('sqlite:///:memory:')
        db.session_create()

        trade = Trade()
        trade.order_id = 1
        trade.buyer_addr = 'buyer_addr'
        trade.seller_addr = 'seller_addr'
        trade.market_hash = 'market_hash'
        trade.AES_key = b'AES_key'
        trade.file_name = 'file_name'

        db.insert(trade)

        count = db.count(trade)
        self.assertEqual(count, 1)

        result = db.query(trade)
        self.assertEqual(result.AES_key, b'AES_key')

        db.delete(result)

        count = db.count(trade)
        self.assertEqual(count, 0)

        result = db.query(trade)
        self.assertEqual(result, None)

        db.session_close()
