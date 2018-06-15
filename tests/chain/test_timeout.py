import time

from cpchain.chain.models import OrderInfo
from cpchain.crypto import RSACipher, get_addr_from_public_key
from cpchain.account import Accounts

order_id = 0
time_allowed = 1000

def test_place_order(bAgent):
    sellerAccount = get_addr_from_public_key(Accounts()[1].public_key)
    proxyAccount = get_addr_from_public_key(Accounts()[2].public_key)

    buyer_rsa_pubkey = RSACipher.load_public_key()
    order_info = OrderInfo(
        desc_hash=bytes([0, 1, 2, 3] * 8),
        buyer_rsa_pubkey=buyer_rsa_pubkey,
        seller=bAgent.web3.toChecksumAddress(sellerAccount),
        proxy=bAgent.web3.toChecksumAddress(proxyAccount),
        secondary_proxy=bAgent.web3.toChecksumAddress(proxyAccount),
        proxy_value=10,
        value=20,
        time_allowed=time_allowed
    )
    global order_id
    order_id = bAgent.place_order(order_info)
    #assert order_id == 1
    test_record = bAgent.query_order(order_id)
    assert test_record[0] == bytes([0, 1, 2, 3] * 8)
    assert test_record[2] == bAgent.account
    # Check state is Created
    assert test_record[10] == 0

def test_seller_confirm_order(sAgent):
    sAgent.confirm_order(order_id)
    test_record = sAgent.query_order(order_id)
    assert test_record[10] == 1

def test_proxy_fetched(pAgent):
    assert pAgent.check_order_is_ready(order_id)
    pAgent.claim_fetched(order_id)
    test_record = pAgent.query_order(order_id)
    assert test_record[10] == 2

def test_proxy_delivered(pAgent):
    pAgent.claim_delivered(order_id, bytes([0, 1, 2, 3] * 8))
    test_record = pAgent.query_order(order_id)
    assert test_record[10] == 3


def test_seller_claim_timeout(sAgent):
    time.sleep(time_allowed + 5)
    sAgent.claim_timeout(order_id)
    test_record = sAgent.query_order(order_id)
    # Check time out is emitted and order is finished
    assert test_record[10] == 5

