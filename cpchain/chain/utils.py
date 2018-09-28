import json
import pathlib

from web3 import Web3, TestRPCProvider, HTTPProvider
from web3.contract import ConciseContract
from eth_keyfile import extract_key_from_keyfile

from cpchain import config
from cpchain.utils import join_with_root


default_w3 = None

def _set_default_w3():
    global default_w3
    mode = config.chain.mode
    if default_w3 or mode == "dummy":
        return

    if mode == "test":
        provider = TestRPCProvider()
    elif mode == "falcon":
        provider = HTTPProvider(config.chain.falcon_provider_addr)
    elif mode == "local":
        provider = HTTPProvider(config.chain.local_provider_addr)
    else:
        raise RuntimeError("No Provider Found.")
    default_w3 = Web3(provider)
    default_w3.eth.defaultAccount = default_w3.eth.accounts[0]

_set_default_w3()


def read_contract_interface(bin_path, contract_name):
    with open(bin_path) as f:
        filename = "{}.sol".format(pathlib.Path(bin_path).stem)
        data = json.load(f)
        intf = data['contracts'][filename][contract_name]
        return intf


def deploy_contract(bin_path, contract_name, w3=default_w3):
    interface = read_contract_interface(bin_path, contract_name)
    contract = w3.eth.contract(abi=interface['abi'], bytecode=interface['evm']['bytecode']['object'])

    estimated_gas = contract.constructor().estimateGas()
    tx_hash = contract.constructor().transact(dict(gas=estimated_gas))

    # get tx receipt to get contract address
    # tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    address = tx_receipt['contractAddress']


    contract = w3.eth.contract(address=address, abi=interface['abi'], ContractFactoryClass=ConciseContract)
    return contract


def read_contract_address(contract_name):
    with open(join_with_root(config.chain.registrar_json)) as f:
        contracts = json.load(f)
    return contracts[contract_name]


def load_private_key_from_keystore(key_path, password='password'):
    key_bytes = extract_key_from_keyfile(key_path, password)
    return key_bytes
