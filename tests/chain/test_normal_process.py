from cpchain.chain.models import OrderInfo


test_trans_id = 0
time_allowed = 60


def test_place_order(btrans):
    order_info = OrderInfo(
        desc_hash=bytes([0, 1, 2, 3] * 8),
        seller=btrans.web3.eth.defaultAccount,
        proxy=btrans.web3.eth.defaultAccount,
        secondary_proxy=btrans.web3.eth.defaultAccount,
        proxy_value=10,
        value=20,
        time_allowed=time_allowed
    )
    global test_trans_id
    test_trans_id = btrans.place_order(order_info)
    assert test_trans_id == 0
    test_record = btrans.query_order(test_trans_id)
    assert bytes(test_record[0], encoding="utf8") == bytes([0, 1, 2, 3] * 8)
    assert test_record[2] == btrans.web3.eth.defaultAccount
    # Check state is Created
    assert test_record[9] == 0


def test_relay_claim(ptrans):
    ptrans.claim_relay(test_trans_id, bytes([2, 3, 4, 5] * 8))
    test_record = ptrans.query_order(test_trans_id)
    # Check state is delivered
    assert test_record[9] == 1


def test_confirm_order(btrans):
    btrans.confirm_order(test_trans_id)
    test_record = btrans.query_order(test_trans_id)
    # Check state is finished after confirmation
    assert test_record[9] == 3
