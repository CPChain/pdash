#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"/..

ROOT_PATH=$(pwd)
export PYTHONPATH=$PYTHONPATH:$ROOT_PATH

python3 cpchain/wallet/ui.py 
