#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"

geth --rpc --rpcaddr 127.0.0.1 --rpcport 8545 --rpcapi admin,debug,eth,miner,net,personal,shh,txpool,web3,ws --ws --wsaddr 127.0.0.1 --wsport 8546 --wsapi admin,debug,eth,miner,net,personal,shh,txpool,web3,ws --datadir ../data_dir --maxpeers 0 --networkid 1234 --port 30303 --ipcpath ../data_dir/geth.ipc --unlock 0x22114f40ed222e83bbd88dc6cbb3b9a136299a23 --password ../password --nodiscover --mine --minerthreads 1

