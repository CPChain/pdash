from cpchain.chain.models import OrderInfo


def test_query_order():
    pass


def test_place_order(btrans):
    order_info = OrderInfo(
        desc_hash=bytearray([0, 1, 2, 3] * 8),
        seller=bytearray([1] * 20),
        proxy=bytearray([1] * 20),
        secondary_proxy=bytearray([1] * 20),
        proxy_value=10,
        value=20
    )
    test_trans_id = btrans.place_order(order_info)
    assert test_trans_id == 0
    test_record = btrans.query_order(test_trans_id)
    assert bytes(test_record[0], encoding="utf8") == bytearray([0, 1, 2, 3] * 8)
    assert test_record[2] == '0x' + bytearray([1] * 20).hex()


def test_withdraw_order(btrans):
    pass


def test_relay_claim():
    pass


def test_confirm_order():
    pass


def test_dispute():
    pass


def test_seller_claim_timeout():
    pass


def test_proxy_claim_relay():
    pass


def test_handle_dispute():
    pass
