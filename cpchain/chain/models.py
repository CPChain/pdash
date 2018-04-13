import collections

order_fields = ['desc_hash', 'buyer_rsa_pubkey', 'seller', 'proxy', 'secondary_proxy', 'proxy_value', 'value', 'time_allowed']
OrderInfo = collections.namedtuple('OrderInfo', order_fields)

# from typing import NamedTuple
# class OrderInfo(NamedTuple):
#     desc_hash: bytearray
#     seller: bytearray
#     proxy: bytearray
#     secondary_proxy: bytearray
#     proxy_value: int
#     value: int
#     time_allowed: int


