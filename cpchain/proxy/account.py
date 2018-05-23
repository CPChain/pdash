from cpchain.account import Accounts
from cpchain.crypto import ECCipher

def get_proxy_id():
    account = Accounts()[0]

    return ECCipher.get_address_from_public_key(
        account.public_key)
