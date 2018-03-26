import json

from web3 import Web3, RPCProvider, TestRPCProvider

from cpchain import config


class DefaultWeb3:
    def __init__(self):
        self.web3 = None

    def _set_web3(self):
        if self.web3 is None:
            if config.chain.is_test:
                provider = TestRPCProvider()
            else:
                provider = RPCProvider(config.chain.rpc_provider_addr)
            self.web3 = Web3(provider)
            self.web3.eth.defaultAccount = self.web3.eth.accounts[0]

    def __getattr__(self, name):
        self._set_web3()
        return getattr(self.web3, name)


default_web3 = DefaultWeb3()


def read_contract_interface(contract_name):
    with open(config.chain.contract_json) as f:
        all_contracts = json.load(f)
        contract_interface = all_contracts['<stdin>:' + contract_name]
    return contract_interface


def read_contract_address(contract_name):
    with open(config.chain.registrar_json) as f:
        contracts = json.load(f)
    return bytes.fromhex(contracts[contract_name][2:])


def deploy_contract(contract_name, web3=default_web3):
    contract_interface = read_contract_interface(contract_name)
    new_contract = web3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    # get transaction hash from deployed contract, let web3 estimate gas for this transaction
    tx_hash = new_contract.deploy(transaction={'from': web3.eth.accounts[0]})
    # get tx receipt to get contract address
    tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
    contract_address = tx_receipt['contractAddress']
    with open(config.chain.registrar_json, 'w') as f:
        f.write(json.dumps(dict({contract_name: contract_address})))
    new_contract.address = contract_address
    return new_contract
