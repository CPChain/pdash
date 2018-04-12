import json, os

from cpchain.chain.utils import default_web3, read_contract_interface
from cpchain import config, root_dir


def deploy_contract(contract_name, web3=default_web3):
    contract_interface = read_contract_interface(contract_name)
    new_contract = web3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    
    # get transaction hash from deployed contract, let web3 estimate gas for this transaction
    tx_hash = new_contract.deploy(transaction={'from': web3.eth.accounts[0]})

    # get tx receipt to get contract address
    # tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

    contract_address = tx_receipt['contractAddress']
    with open(config.chain.registrar_json, 'w') as f:
        f.write(json.dumps(dict({contract_name: contract_address})))
    new_contract.address = contract_address
    return new_contract


def main():
    os.chdir(root_dir)
    address = deploy_contract(config.chain.core_contract)
    print("contract address: " + str(address))


if __name__ == "__main__":
    main()
