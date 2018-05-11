from cryptography.hazmat.primitives.serialization import load_der_public_key, load_pem_public_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from eth_utils import to_bytes

from cpchain.wallet.fs import *
from cpchain.chain.agents import *
from cpchain import chain, config, root_dir
from cpchain.utils import join_with_root, Encoder
from cpchain.chain.models import OrderInfo
from cpchain.crypto import RSACipher, ECCipher, pub_key_der_to_addr, get_addr_from_public_key


def test_server_chain():
    os.chdir(root_dir)
    server_web3 = chain.default_web3
    # chain.utils.deploy_contract(config.chain.core_contract)
    buyertrans = BuyerAgent(server_web3, config.chain.core_contract)
    print(server_web3.eth.defaultAccount)
    # desc_hash_base64 = 'AQkKqDxtNIRJ+1V82J5lP2/fRj/zbJ+2n0GzUF52Wsc='
    # desc_hash = Encoder.str_to_base64_byte(desc_hash_base64)
    # public_key = RSACipher.load_public_key()
    # print('pubkey ' + str(len(public_key)))
    # order_info = OrderInfo(
    #     desc_hash=desc_hash,
    #     buyer_rsa_pubkey=public_key,
    #     seller=buyertrans.web3.eth.defaultAccount,
    #     proxy=buyertrans.web3.eth.defaultAccount,
    #     secondary_proxy=buyertrans.web3.eth.defaultAccount,
    #     proxy_value=10,
    #     value=20,
    #     time_allowed=100
    # )
    # test_server_id = buyertrans.place_order(order_info)
    # print(test_server_id)
    # buyertrans.withdraw_order(test_server_id)
    # print(buyertrans.query_order(test_server_id))
    order_num = buyertrans.get_order_num()
    print(order_num)
    latest_order_info = buyertrans.query_order(order_num - 1)
    private_key_file_path = join_with_root(config.wallet.private_key_file)
    password_path = join_with_root(config.wallet.private_key_password_file)
    with open(password_path) as f:
        password = f.read()
    priv_key, pub_key = ECCipher.load_key_pair_from_private_key(private_key_file_path, password)
    pub_key_bytes = Encoder.str_to_base64_byte(pub_key)
    pub_key_loaded = load_der_public_key(pub_key_bytes, backend=default_backend())
    # print(Encoder.str_to_base64_byte(pub_key))
    # print(len(Encoder.str_to_base64_byte(pub_key)))
    # print(pub_key_bytes_to_addr(Encoder.str_to_base64_byte(pub_key)))
    # print(len(pub_key_bytes_to_addr(Encoder.str_to_base64_byte(pub_key))))
    print(get_addr_from_public_key(pub_key_loaded))
    print(to_bytes(hexstr=latest_order_info[2]))
    print(len(to_bytes(hexstr=latest_order_info[2])))


    # market_hash = 'qHZP3XChYo3y7ZUWVVdu1LHB2s9AYD8jPILVhgSQ5U4='
    # raw_aes_key = session.query(FileInfo.aes_key).filter(FileInfo.market_hash == market_hash).all()[0][0]
    # print(type(raw_aes_key))
    # print(len(raw_aes_key))
    # buyer_rsa_pubkey = latest_order_info[1]
    # encrypted_aes_key = load_der_public_key(buyer_rsa_pubkey, backend=default_backend()).encrypt(
    #     raw_aes_key,
    #     padding.OAEP(
    #         mgf=padding.MGF1(algorithm=hashes.SHA256()),
    #         algorithm=hashes.SHA256(),
    #         label=None
    #     )
    # )
    # print(str(type(encrypted_aes_key)) + ' $$ ' + str(len(encrypted_aes_key)))
    # file_hash = session.query(FileInfo.hashcode) \
    #     .filter(FileInfo.market_hash == market_hash) \
    #     .all()[0][0]
    # print(file_hash)
    # print(type(file_hash))
    # print(len(file_hash))


def main():
    test_server_chain()


if __name__ == '__main__':
    main()
