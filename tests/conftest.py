import pytest

import os
pwd = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(pwd, '../cpchain/chain/assets/'))

from cpchain.chain import trans


@pytest.fixture()
def contract(chain):
    return chain.provider.get_or_deploy_contract('xxx')


@pytest.fixture()
def btrans(chain):
    trans_obj = trans.BuyerTrans(chain, "")

    return trans_obj


@pytest.fixture()
def strans(chain):
    trans_obj = None

    return trans_obj


@pytest.fixture()
def ptrans(chain):
    trans_obj = None
    return trans_obj
