import pytest

import os
pwd = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(pwd, '../cpchain/chain/assets/'))

from cpchain.chain import trans


@pytest.fixture()
def contract(chain):
    contract_name = 'Trading'
    return chain.provider.get_or_deploy_contract('Trading')


@pytest.fixture()
def btrans(chain, contract):
    trans_obj = trans.BuyerTrans(chain, contract)
    return trans_obj


@pytest.fixture()
def strans(chain, contract):
    trans_obj = trans.SellerTrans(chain, contract)
    return trans_obj


@pytest.fixture()
def ptrans(chain, contract):
    trans_obj = trans.ProxyTrans(chain, contract)
    return trans_obj
