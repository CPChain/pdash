from cpchain.chain.models import OrderInfo
from cpchain.crypto import RSACipher

test_trans_id = 0
time_allowed = 60


def test_place_order(btrans):
    buyer_rsa_pubkey = RSACipher.load_public_key()
    order_info = OrderInfo(
        desc_hash=bytes([0, 1, 2, 3] * 8),
        buyer_rsa_pubkey=buyer_rsa_pubkey,
        seller=btrans.web3.eth.defaultAccount,
        proxy=btrans.web3.eth.defaultAccount,
        secondary_proxy=btrans.web3.eth.defaultAccount,
        proxy_value=10,
        value=20,
        time_allowed=time_allowed
    )
    global test_trans_id
    test_trans_id = btrans.place_order(order_info)
    assert test_trans_id == 1
    test_record = btrans.query_order(test_trans_id)
    assert test_record[0] == bytes([0, 1, 2, 3] * 8)
    assert test_record[2] == btrans.web3.eth.defaultAccount
    # Check state is Created
    assert test_record[10] == 0


def test_relay_claim(ptrans):
    ptrans.claim_relay(test_trans_id, bytes([2, 3, 4, 5] * 8))
    test_record = ptrans.query_order(test_trans_id)
    # Check state is delivered
    assert test_record[10] == 1


def test_confirm_order(btrans):
    btrans.confirm_order(test_trans_id)
    test_record = btrans.query_order(test_trans_id)
    # Check state is finished after confirmation
    assert test_record[10] == 3
