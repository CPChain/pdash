from cpchain.wallet.fs import *
from cpchain.wallet.db import *
from cpchain.proxy.ipfs import *


def test_file_db():
    create_table()
    delete_file("asdf")
    fileinfo0 = FileInfo(hashcode='abcdefg', name="asdf", path="iasdf", size=3234, remote_type="asdf", remote_uri="asdfadsf")
    add_file(fileinfo0)
    # print(get_file_names())
    print(get_file_list()[0].name)


def test_encryption_decryption():
    create_table()
    delete_file("shakespeare")
    fileinfo1 = FileInfo(hashcode=0x1234567, name="shakespeare", path="/Users/renfei/Documents/projects/cpchain/tools/assets/encrypted.txt", size=3234, remote_type="asdf", remote_uri="asdfadsf")
    add_file(fileinfo1)
    print(get_file_names())
    fin_path = '/Users/renfei/Documents/projects/cpchain/tools/assets/shakespeare.txt'
    fout_path = '/Users/renfei/Documents/projects/cpchain/tools/assets/encrypted.txt'
    encrypt_file(fin_path, fout_path)

    fin_path_new = '/Users/renfei/Documents/projects/cpchain/tools/assets/decrypted.txt'
    decrypt_file(fout_path, fin_path_new)


def test_upload_ipfs():
    fin_path = '/Users/renfei/Documents/projects/cpchain/tools/assets/shakespeare.txt'
    file_hash = upload_file_ipfs(fin_path)
    print(file_hash)


def main():
    # test_file_db()
    # test_encryption_decryption()
    test_upload_ipfs()


if __name__ == '__main__':
    main()
