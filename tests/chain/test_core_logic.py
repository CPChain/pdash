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
    # order_info = OrderInfo(desc_hash=0x1, seller=, proxy=, secondary_proxy=, pay_ratio=)
    # btrans.place_order()

    # assert False
    import ipdb; ipdb.set_trace()
