import os
import os.path as osp

import pytest

from cpchain import chain, config, root_dir
from cpchain.account import Accounts
from cpchain.crypto import get_addr_from_public_key

# NB, we switch to the package root dir
os.chdir(root_dir)
accounts = Accounts()


@pytest.fixture(scope="module")
def contract_name():
    w3 = chain.utils.default_w3
    bin_path = chain.utils.join_with_root(config.chain.contract_bin_path)
    new_contract_name = config.chain.contract_name

    chain.utils.deploy_contract(bin_path, new_contract_name, w3)
    return new_contract_name


@pytest.fixture(scope="module")
def bAgent(contract_name):
    buyer_web3 = chain.utils.default_w3
    bin_path = chain.utils.join_with_root(config.chain.contract_bin_path)
    account = get_addr_from_public_key(accounts[0].public_key)

    agent_obj = chain.agents.BuyerAgent(buyer_web3, bin_path, contract_name, account=account)
    return agent_obj


@pytest.fixture()
def sAgent(contract_name):
    seller_web3 = chain.utils.default_w3
    bin_path = chain.utils.join_with_root(config.chain.contract_bin_path)
    account = get_addr_from_public_key(accounts[1].public_key)
    agent_obj = chain.agents.SellerAgent(seller_web3, bin_path, contract_name, account=account)
    return agent_obj


@pytest.fixture()
def pAgent(contract_name):
    proxy_web3 = chain.utils.default_w3
    bin_path = chain.utils.join_with_root(config.chain.contract_bin_path)
    account = get_addr_from_public_key(accounts[2].public_key)
    agent_obj = chain.agents.ProxyAgent(proxy_web3, bin_path, contract_name, account=account)
    return agent_obj

@pytest.fixture()
def tAgent(contract_name):
    trent_web3 = chain.utils.default_w3
    bin_path = chain.utils.join_with_root(config.chain.contract_bin_path)
    agent_obj = chain.agents.TrentAgent(trent_web3, bin_path, contract_name,)
    return agent_obj
