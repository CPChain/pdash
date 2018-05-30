.PHONY: lint test test-chain test-proxy

PYLINT = python3 -m pylint

lint:
	$(PYLINT) cpchain

test: test-chain test-proxy test-market

test-proxy:
	python3 -m twisted.trial ./tests/proxy/test_server.py

test-chain:
	py.test ./tests/chain

test-market:
	@exit 1




