import os
import os.path as osp

import pytest

from cpchain import chain, config, root_dir


# NB, we switch to the package root dir
os.chdir(root_dir)


@pytest.fixture(scope="module")
def contract_name():
    w3 = chain.utils.default_w3
    bin_path = chain.utils.join_with_root(config.chain.contract_bin_path)
    new_contract_name = config.chain.contract_name

    chain.utils.deploy_contract(bin_path, new_contract_name, w3)
    return new_contract_name


@pytest.fixture(scope="module")
def btrans(contract_name):
    buyer_web3 = chain.utils.default_w3
    print('buyer: defaultAccount:{}'.format(buyer_web3.eth.defaultAccount))
    bin_path = chain.utils.join_with_root(config.chain.contract_bin_path)
    trans_obj = chain.agents.BuyerAgent(buyer_web3, bin_path, contract_name)
    return trans_obj


@pytest.fixture()
def strans(contract_name):
    seller_web3 = chain.utils.default_w3
    print('seller: defaultAccount:{}'.format(seller_web3.eth.defaultAccount))
    bin_path = chain.utils.join_with_root(config.chain.contract_bin_path)
    trans_obj = chain.agents.SellerAgent(seller_web3, bin_path, contract_name)
    return trans_obj


@pytest.fixture()
def ptrans(contract_name):
    proxy_web3 = chain.utils.default_w3
    print('seller: defaultAccount:{}'.format(proxy_web3.eth.defaultAccount))
    bin_path = chain.utils.join_with_root(config.chain.contract_bin_path)
    trans_obj = chain.agents.ProxyAgent(proxy_web3, bin_path, contract_name)
    return trans_obj
