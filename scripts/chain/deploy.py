import json

from cpchain.chain.utils import deploy_contract
from cpchain import config
from cpchain.utils import join_with_root


def main():
    bin_path = join_with_root(config.chain.contract_bin_path)
    contract_name = config.chain.contract_name
    contract = deploy_contract(bin_path, contract_name)

    registrar_path = join_with_root(config.chain.registrar_json)
    with open(registrar_path, 'w') as f:
        f.write(json.dumps(dict({contract_name: contract.address})))

    print("contract address: %s" % contract.address)


if __name__ == "__main__":
    import sys
    from getpass import getpass

    from cpchain.chain.utils import default_w3 as web3

    if len(sys.argv) != 2:
        print("Need pre-funded account as sender, i.e. 4a8f38c0d4b398ae3253689808454c88e8a16376")
        sys.exit(1)

    account = web3.toChecksumAddress(sys.argv[1])
    passwd = getpass('please input keyphrase for your account: ')

    web3.personal.unlockAccount(account, passwd)

    # deploy_contract() uses web3.eth.defaultAccount as sender
    web3.eth.defaultAccount = account

    main()

    web3.personal.lockAccount(account)
