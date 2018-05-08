import sys
import json
import os.path as osp

# cf. http://tinyurl.com/yd7mbzp3
from solc import compile_standard

from cpchain import config
from cpchain.utils import join_with_root


def compile_contract(src_path, abi_path):
    # cf. http://tinyurl.com/yap75nl8
    sol_map = {
        "language": "Solidity",
        "sources": {},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode"]
                }
            }
        }
    }

    basename = osp.basename(src_path)
    d = sol_map["sources"][basename] = {}
    d["urls"] = [src_path]
    output = compile_standard(sol_map, allow_paths=osp.dirname(src_path))

    with open(abi_path, mode='w') as f:
        f.write(json.dumps(output))


def main():
    if len(sys.argv) != 3:
        src_path = join_with_root(config.chain.contract_src_path)
        abi_path = join_with_root(config.chain.contract_bin_path)
    else:
        src_path = sys.argv[1]
        abi_path = sys.argv[2]

    compile_contract(src_path, abi_path)


if __name__ == "__main__":
    main()
