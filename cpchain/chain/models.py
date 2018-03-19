from typing import NamedTuple

class OrderInfo(NamedTuple):
    desc_hash: int
    seller: int
    proxy: int
    secondary_proxy: int
    proxy_value: int
    value: int
