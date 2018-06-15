from cpchain.chain.models import OrderInfo
from cpchain.crypto import RSACipher, get_addr_from_public_key
from cpchain.account import Accounts

order_id = 0
time_allowed = 200000

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

def test_withdraw_order(bAgent):
    bAgent.withdraw_order(order_id)
    test_record = bAgent.query_order(order_id)
    assert test_record[10] == 9
