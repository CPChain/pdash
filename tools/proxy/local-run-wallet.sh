#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"/../../

export PROXY_LOCAL_RUN=1

python3 cpchain/wallet/wallet.py
