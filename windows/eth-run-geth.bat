cd %CD%\..\eth

set LISTEN_ADDRESS="127.0.0.1"


.\bin\geth.exe --rpc --rpcaddr %LISTEN_ADDRESS% --rpcport 8545 --rpcapi admin,debug,eth,miner,net,personal,shh,txpool,web3,ws --ws --wsaddr %LISTEN_ADDRESS% --wsport 8546 --wsapi admin,debug,eth,miner,net,personal,shh,txpool,web3,ws --datadir .\data_dir --maxpeers 0 --networkid 1234 --port 30303 --ipcpath .\data_dir\geth.ipc --unlock 0x22114f40ed222e83bbd88dc6cbb3b9a136299a23,0x7975bcf2faefec0dae6ccc82a66f89b12f23c747,0xb75b727eafdb8723ed1620834134592e4470c2a0,0xd988c09feef6c64e798fbb6b7cd6fa731b91fdbf,0x93aee1dd025e0ab95d12a401cacac71b383220c0,0x2af2e6a7da5c788f6a73abf67bb8acb809d7ff54,0x518d5e6f3330cc65b6a13babb51e252c7b25cea3,0xfae7d91a3ce5d4693ac51fb39bd0ed5db157c9ca,0x7db76c59620786b87a0e8157ff81bf91250d8c87,0xbe76a83b64ceb0dd04f591f074977efaca799f49,0x2a8fe50954a99eb0e6c7f5184a6204d5ef1e3190,0x12ea9f6fd78ea95ce4dd2326fe85a19934f8469c --password .\data_dir\keystore\password --nodiscover --mine --minerthreads 1 
