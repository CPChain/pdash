cd %CD%\..\eth

bin\geth.exe --rpc --rpcaddr 127.0.0.1 --rpcport 8545 --rpcapi admin,debug,eth,miner,net,personal,shh,txpool,web3,ws --ws --wsaddr 127.0.0.1 --wsport 8546 --wsapi admin,debug,eth,miner,net,personal,shh,txpool,web3,ws --datadir .\data_dir --maxpeers 0 --networkid 1234 --port 30303 --ipcpath .\data_dir\geth.ipc --nodiscover --mine --minerthreads 3 init .\genesis.json

