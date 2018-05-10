from cpchain.wallet import net
import pytest

@pytest.fixture()
def market_client():
    market_client = net.MarketClient('wallet')
    return market_client

def test_query_carousel(market_client):
