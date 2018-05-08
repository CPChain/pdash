.PHONY: 

PYLINT = python3 -m pylint

lint:
	pylint cpchain

test-proxy:
	python3 -m twisted.trial ./tests/proxy/test_server.py
