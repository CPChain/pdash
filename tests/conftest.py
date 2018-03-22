import os
import os.path as osp

import pytest

from cpchain import chain, config, root_dir


# NB, we switch to the package root dir
os.chdir(root_dir)


@pytest.fixture(scope="module")
def contract():
    contract_name = config.chain.core_contract
    contract_interface = chain.utils.read_contract_interface(config.chain.contract_json, contract_name)
    contract_obj = chain.utils.deploy_contract(contract_interface)
    return contract_obj


@pytest.fixture(scope="module")
def btrans(w3, contract):
    trans_obj = chain.trans.BuyerTrans(w3, contract, utils.w3.eth.accounts[0])
    return trans_obj


@pytest.fixture()
def strans(w3, contract):
    trans_obj = chain.trans.SellerTrans(w3, contract, utils.w3.eth.accounts[0])
    return trans_obj


@pytest.fixture()
def ptrans(w3, contract):
    trans_obj = chain.trans.ProxyTrans(w3, contract, utils.w3.eth.accounts[0])
    return trans_obj
