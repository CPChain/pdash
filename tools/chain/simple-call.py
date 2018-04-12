from cpchain.wallet.fs import *
from cpchain.wallet.db import *
from cpchain.chain.trans import *
from cpchain import chain, config, root_dir
from cpchain.chain.models import OrderInfo


def test_server_chain():
    os.chdir(root_dir)
    server_web3 = chain.default_web3
    # chain.utils.deploy_contract(config.chain.core_contract)
    buyertrans = BuyerTrans(server_web3, config.chain.core_contract)
    print(server_web3.eth.defaultAccount)
    order_info = OrderInfo(
        desc_hash=bytearray([0, 1, 2, 3] * 8),
        seller=buyertrans.web3.eth.defaultAccount,
        proxy=buyertrans.web3.eth.defaultAccount,
        secondary_proxy=buyertrans.web3.eth.defaultAccount,
        proxy_value=10,
        value=20,
        time_allowed=10
    )
    # test_server_id = buyertrans.place_order(order_info)
    # print(test_server_id)
    order_num = buyertrans.get_order_num()
    print(order_num)


def main():
    # test_file_db()
    # test_encryption_decryption()
    # test_upload_ipfs()
    # test_buyer_table()
    test_server_chain()


if __name__ == '__main__':
    main()
