#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"

sudo apt install -y python3-pyqt5

sudo apt install -y python3-twisted python3-treq

sudo apt install -y python3-protobuf
# compiler is only needed for dev.
# sudo apt install -y protobuf-compiler python3-protobuf

sudo apt install -y python3-cryptography python3-sqlalchemy python3-toml python3-boto3

sudo apt install -y python3-flake8

pip3 install -Ur requirements-dev.txt
