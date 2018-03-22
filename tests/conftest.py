import os
import os.path as osp

import pytest


from cpchain import chain, config, root_dir


# NB, we switch to the package root dir
os.chdir(root_dir)


@pytest.fixture(scope="module")
def w3():
    utils.w3.eth.defaultAccout = utils.w3.eth.accounts[0]
    return utils.w3


@pytest.fixture(scope="module")
def contract(w3):
    # w3.eth.defaultAccout = w3.eth.accounts[0]
    contract_name = config.chain.core_contract
    test_contract = utils.read_contract_interface(config.chain.contract_build_dir, contract_name)
    contract_obj = utils.deploy_contract(test_contract)
    return contract_obj


@pytest.fixture(scope="module")
def btrans(w3, contract):
    trans_obj = trans.BuyerTrans(w3, contract, utils.w3.eth.accounts[0])
    return trans_obj


@pytest.fixture()
def strans(w3, contract):
    trans_obj = trans.SellerTrans(w3, contract, utils.w3.eth.accounts[0])
    return trans_obj


@pytest.fixture()
def ptrans(w3, contract):
    trans_obj = trans.ProxyTrans(w3, contract, utils.w3.eth.accounts[0])
    return trans_obj
