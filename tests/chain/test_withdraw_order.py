from cpchain.chain.models import OrderInfo
from cpchain.crypto import RSACipher, get_addr_from_public_key
from cpchain.account import Accounts

test_trans_id = 0
time_allowed = 200000

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

def test_withdraw_order(btrans):
    btrans.withdraw_order(test_trans_id)
    test_record = btrans.query_order(test_trans_id)
    assert test_record[10] == 9
