import sys
import json
import os.path as osp

from solc import compile_source

from cpchain import config, root_dir


# A naive approach without sufficient error handling
def compile_solidity(contract_src_dir, contract_build_dir):
    # First read the source code and compile the code
    with open(contract_src_dir, "r") as file:
        contract_source_code = file.read()
    # Then extract the compiled contract and write contract interface to local file
    compiled_sol = compile_source(contract_source_code)
    with open(contract_build_dir, "w") as file:
        file.write(json.dumps(compiled_sol))


def main():
    if len(sys.argv) < 3:
        compile_solidity(
            osp.join(root_dir, config.chain.contract_src_dir),
            osp.join(root_dir, config.chain.contract_json)
        )
    else:
        compile_solidity(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
