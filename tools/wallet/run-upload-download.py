from cpchain.wallet.db import *
from cpchain.wallet.fs import *





def proxy_upload_file():
    new_buyer_file_info = BuyerFileInfo(order_id=0, market_hash='hash',
                                        file_title='title', is_downloaded=False)
    add_file(new_buyer_file_info)


def main():
    proxy_upload_file()


if __name__ == '__main__':
    main()
