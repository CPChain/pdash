from cpchain.chain.models import OrderInfo
from cpchain.crypto import RSACipher, get_addr_from_public_key
from cpchain.account import Accounts

test_trans_id = 0
time_allowed = 200000

def test_proxy_deposit(ptrans):

    balance = ptrans.query_deposit()
    value = 1000
    ptrans.deposit(value)
    assert ptrans.query_deposit() == balance + value

    withdraw = 499
    ptrans.withdraw(withdraw)
    assert ptrans.query_deposit() == balance + value - withdraw

def test_place_order(btrans):
    sellerAccount = get_addr_from_public_key(Accounts()[1].public_key)
    proxyAccount = get_addr_from_public_key(Accounts()[2].public_key)

    buyer_rsa_pubkey = RSACipher.load_public_key()
    order_info = OrderInfo(
        desc_hash=bytes([0, 1, 2, 3] * 8),
        buyer_rsa_pubkey=buyer_rsa_pubkey,
        seller=btrans.web3.toChecksumAddress(sellerAccount),
        proxy=btrans.web3.toChecksumAddress(proxyAccount),
        secondary_proxy=btrans.web3.toChecksumAddress(proxyAccount),
        proxy_value=10,
        value=20,
        time_allowed=time_allowed
    )
    global test_trans_id
    test_trans_id = btrans.place_order(order_info)
    #assert test_trans_id == 1
    test_record = btrans.query_order(test_trans_id)
    assert test_record[0] == bytes([0, 1, 2, 3] * 8)
    assert test_record[2] == btrans.account
    # Check state is Created
    assert test_record[10] == 0

def test_seller_confirm_order(strans):
    strans.confirm_order(test_trans_id)
    test_record = strans.query_order(test_trans_id)
    assert test_record[10] == 1

def test_proxy_fetched(ptrans):
    assert ptrans.check_order_is_ready(test_trans_id)
    ptrans.claim_fetched(test_trans_id)
    test_record = ptrans.query_order(test_trans_id)
    assert test_record[10] == 2

def test_proxy_delivered(ptrans):
    ptrans.claim_delivered(test_trans_id, bytes([0, 1, 2, 3] * 8))
    test_record = ptrans.query_order(test_trans_id)
    assert test_record[10] == 3

def test_buyer_dispute(btrans):
    btrans.dispute(test_trans_id)
    test_record = btrans.query_order(test_trans_id)
    assert test_record[10] == 8
    test_dispute_record = btrans.fetch_dispute_result(test_trans_id)
    assert test_dispute_record[7] == 0

def test_proxy_handle_dispute(ptrans):
    ptrans.handle_dispute(test_trans_id, True)
    test_dispute_record = ptrans.fetch_dispute_result(test_trans_id)
    assert test_dispute_record[0] == test_trans_id
    assert test_dispute_record[1] is False
    assert test_dispute_record[2] is True
    assert test_dispute_record[3] is False
    assert test_dispute_record[4] is False
    assert test_dispute_record[5] is False
    assert test_dispute_record[7] == 1

def test_buyer_agree(btrans):
    btrans.confirm_dispute(test_trans_id, True)
    test_dispute_record = btrans.fetch_dispute_result(test_trans_id)
    assert test_dispute_record[0] == test_trans_id
    assert test_dispute_record[1] is False
    assert test_dispute_record[2] is True
    assert test_dispute_record[3] is False
    assert test_dispute_record[4] is True
    assert test_dispute_record[5] is False
    assert test_dispute_record[7] == 1

def test_seller_agree(strans):
    strans.confirm_dispute(test_trans_id, False)
    test_dispute_record = strans.fetch_dispute_result(test_trans_id)
    assert test_dispute_record[0] == test_trans_id
    assert test_dispute_record[1] is False
    assert test_dispute_record[2] is True
    assert test_dispute_record[3] is False
    assert test_dispute_record[4] is True
    assert test_dispute_record[5] is False
    assert test_dispute_record[7] == 1

    test_record = strans.query_order(test_trans_id)
    assert test_record[10] == 8

def test_trent_fetch(ttrans):
    print(ttrans.fetch_unhandled_disputes(0, 3))
    test_trans_id = ttrans.fetch_unhandled_disputes(0, 4)[0]
    ttrans.handle_dispute(test_trans_id, True, False, True)

    test_record = ttrans.query_order(test_trans_id)
    assert test_record[10] == 5

    test_dispute_record = ttrans.fetch_dispute_result(test_trans_id)
    assert test_dispute_record[7] == 2
