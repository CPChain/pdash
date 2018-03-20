from solc import compile_source
import sys
import json


# A naive approach without sufficient error handling
def compile_solidity(source_path, output_path):
    # First read the source code and compile the code
    contract_source_file = open(source_path, "r")
    contract_source_code = contract_source_file.read()
    contract_source_file.close()
    # Then extract the compiled contract and write contract interface to local file
    compiled_sol = compile_source(contract_source_code)
    compiled_file = open(output_path, "w")
    compiled_file.write(json.dumps(compiled_sol))
    compiled_file.close()


def main():
    if len(sys.argv) < 3:
        print("Please input right parameters.")
        return -1
    else:
        compile_solidity(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()

