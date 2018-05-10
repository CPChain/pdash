import os

import pytest

from cpchain import chain, config, root_dir


# NB, we switch to the package root dir
os.chdir(root_dir)

@pytest.fixture(scope="module")
def contract_name():
    new_contract_name = config.chain.contract_name
    chain.utils.deploy_contract(new_contract_name)
    return new_contract_name


@pytest.fixture()
def btrans(contract_name):
    buyer_web3 = chain.utils.default_w3
    print('buyer: defaultAccount:'.format(buyer_web3.eth.defaultAccount))
    trans_obj = chain.trans.BuyerTrans(buyer_web3, contract_name=contract_name)
    return trans_obj


@pytest.fixture()
def strans(contract_name):
    seller_web3 = chain.utils.default_w3
    print('seller: defaultAccount:'.format(seller_web3.eth.defaultAccount))
    trans_obj = chain.trans.SellerTrans(chain.utils.default_w3, contract_name=contract_name)
    return trans_obj


@pytest.fixture()
def ptrans(contract_name):
    proxy_web3 = chain.utils.default_w3
    print('seller: defaultAccount:'.format(proxy_web3.eth.defaultAccount))
    trans_obj = chain.trans.ProxyTrans(chain.utils.default_w3, contract_name=contract_name)
    return trans_obj