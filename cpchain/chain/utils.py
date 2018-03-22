import json

from web3 import Web3, HTTPProvider, TestRPCProvider

from cpchain import config


if config['chain']['mode'] == "test":
    w3 = Web3(TestRPCProvider())
else:
    w3 = Web3(HTTPProvider(config['chain']['default_provider']))


def read_contract_interface(interface_path, contract_name):
    with open(interface_path, "r") as file:
        all_contracts = json.load(file)
        contract_interface = all_contracts['<stdin>:' + contract_name]
    return contract_interface


def deploy_contract(contract_interface):
    new_contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    # Get transaction hash from deployed contract, let web3 estimate gas for this transaction
    tx_hash = new_contract.deploy(transaction={'from': w3.eth.accounts[0]})
    # Get tx receipt to get contract address
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    contract_address = tx_receipt['contractAddress']
    new_contract.address = contract_address
    return new_contract, contract_address


