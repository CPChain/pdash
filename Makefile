.PHONY: lint test-proxy

PYLINT = python3 -m pylint

lint:
	$(PYLINT) cpchain

test-proxy:
	python3 -m twisted.trial ./tests/proxy/test_server.py
