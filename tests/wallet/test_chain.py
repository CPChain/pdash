import pytest

from cpchain import config

from cpchain.wallet.chain import Handler
from cpchain.chain.agents import BuyerAgent
from cpchain.chain.utils import default_w3


def test_buy_product(mocker):
    buyer = BuyerAgent(default_w3, config.chain.contract_bin_path, config.chain.contract_name)
    mocker.patch.object(buyer, 'place_order')
    Handler.buy_product('msg_hash', 'file_title')
    assert buyer.place_order.callcount == 1

