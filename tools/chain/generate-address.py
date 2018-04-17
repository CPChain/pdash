from eth_keys import keys
from eth_keyfile import extract_key_from_keyfile


from cpchain import config

from cpchain.utils import join_with_root


priv_bytes = extract_key_from_keyfile(join_with_root(config.wallet.private_key_file), open(join_with_root(config.wallet.private_key_password_file)).read())

print(priv_bytes)
priv_key = keys.PrivateKey(priv_bytes)

pub_key = priv_key.public_key
addr = pub_key.to_address()
print(addr)
