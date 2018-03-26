from typing import NamedTuple


class OrderInfo(NamedTuple):
    desc_hash: bytearray
    seller: bytearray
    proxy: bytearray
    secondary_proxy: bytearray
    proxy_value: int
    value: int
    time_allowed: int
