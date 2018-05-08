.PHONY: 

FLAKE = python3 -m flake8

lint:
	pylint cpchain

test-proxy:
	python3 -m twisted.trial ./tests/proxy/test_server.py
