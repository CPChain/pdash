import sys
import json
import os.path as osp

from solc import compile_source

from cpchain import config, root_dir


# A naive approach without sufficient error handling
def compile_solidity(contract_src_dir, contract_build_dir):
    # First read the source code and compile the code
    contract_source_file = open(contract_src_dir, "r")
    contract_source_code = contract_source_file.read()
    contract_source_file.close()
    # Then extract the compiled contract and write contract interface to local file
    compiled_sol = compile_source(contract_source_code)
    compiled_file = open(contract_build_dir, "w")
    compiled_file.write(json.dumps(compiled_sol))
    compiled_file.close()


def main():
    if len(sys.argv) < 3:
        compile_solidity(
            osp.join(root_dir, config['chain']['contract_src_dir']),
            osp.join(root_dir, config['chain']['contract_build_dir'])
        )
    else:
        compile_solidity(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()

