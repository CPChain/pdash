
from cpchain.wallet.fs import *


# def proxy_download_file():
#     get_file_from_proxy(0, 'seller_public_key')


def decrypt_file_buyer():

    raw_aes_key = AESCipher.generate_key()
    cipher = AESCipher(raw_aes_key)
    fin_path = '/Users/renfei/Documents/projects/cpchain/tools/assets/shakespeare.txt'
    fout_path = '/Users/renfei/Documents/projects/cpchain/tools/assets/encrypted.txt'
    cipher.encrypt(fin_path, fout_path)

    ciphered_aes_key = RSACipher.encrypt(raw_aes_key)

    decrypt_file_aes(fout_path, ciphered_aes_key)




def main():
    # proxy_download_file()
    decrypt_file_buyer()


if __name__ == '__main__':
    main()
