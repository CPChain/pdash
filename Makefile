.PHONY: 

FLAKE = python3 -m flake8

lint:
	$(FLAKE) cpchain
