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
    main()
