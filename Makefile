.PHONY: lint test test-chain test-proxy

PYLINT = python3 -m pylint

lint:
	$(PYLINT) cpchain

test: test-common test-chain test-proxy test-market

test-proxy:
	python3 -m twisted.trial ./tests/proxy/test_server.py

test-chain:
	py.test ./tests/chain --junitxml=test_report.xml --cov-report=xml --cov=./

test-market:
	py.test ./cpchain/market --junitxml=test_report.xml --cov-report=xml --cov=./

test-common:
	py.test ./tests --junitxml=test_report.xml --cov-report=xml --cov=./