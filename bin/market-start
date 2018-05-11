#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"/..

ROOT_PATH=$(pwd)
export PYTHONPATH=$PYTHONPATH:$ROOT_PATH

python3 cpchain/market/manage.py runserver 0.0.0.0:8083
