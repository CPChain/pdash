from cpchain.wallet.wallet import Wallet
from cpchain.wallet.net import MarketClient

import pytest

@pytest.fixture()
def market_client():
    from twisted.internet import reactor
    wallet = Wallet(reactor)
    market_client = MarketClient(wallet)
    return market_client

def test_query_carousel(mocker, market_client):
    mock = mocker.patch('treq.get')
    market_client.query_carousel()
    assert mock.called

def test_query_hot_tag(mocker, market_client):
    mock = mocker.patch('treq.get')
    market_client.query_hot_tag()
    assert mock.called

def test_query_promotion(mocker, market_client):
    mock = mocker.patch('treq.get')
    market_client.query_promotion()
    assert mock.called

def test_query_recommend_product(mocker, market_client):
    mock = mocker.patch('treq.get')
    market_client.query_recommend_product()
    assert mock.called

def test_login(mocker, market_client):
    mock = mocker.patch('treq.post')
    market_client.login()
    assert mock.called