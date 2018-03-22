from web3 import Web3

# def test_initiate_order(chain):
#     greeter, _ = chain.provider.get_or_deploy_contract('Greeter')

#     greeting = greeter.call().greet()
#     assert greeting == 'Hello'


# def test_custom_greeting(chain):
#     greeter, _ = chain.provider.get_or_deploy_contract('Greeter')

#     set_txn_hash = greeter.transact().setGreeting('Guten Tag')
#     chain.wait.for_receipt(set_txn_hash)

#     greeting = greeter.call().greet()
#     assert greeting == 'Guten Tag'


from cpchain.chain.models import OrderInfo


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
