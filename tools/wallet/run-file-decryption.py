
from cpchain.wallet.fs import *


# def proxy_download_file():
#     get_file_from_proxy(0, 'seller_public_key')


def decrypt_file_buyer():
    with open(join_with_root(config.wallet.rsa_private_key_password_file), "rb") as f:
        buyer_rsa_private_key_password = f.read()
    with open(join_with_root(config.wallet.rsa_private_key_file), "rb") as key_file:
        buyer_private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=buyer_rsa_private_key_password,
            backend=default_backend()
        )

    raw_aes_key = AESCipher.generate_key()
    cipher = AESCipher(raw_aes_key)
    fin_path = '/Users/renfei/Documents/projects/cpchain/tools/assets/shakespeare.txt'
    fout_path = '/Users/renfei/Documents/projects/cpchain/tools/assets/encrypted.txt'
    cipher.encrypt(fin_path, fout_path)

    ciphered_aes_key = buyer_private_key.public_key().encrypt(
        raw_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    decrypt_file_aes(fout_path, ciphered_aes_key)




def main():
    # proxy_download_file()
    decrypt_file_buyer()


if __name__ == '__main__':
    main()
