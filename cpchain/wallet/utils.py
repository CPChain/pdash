import urllib.parse
from cpchain.crypto import ECCipher, Encoder


def build_url(url, values):
    data = urllib.parse.urlencode(values)
    new_url = url + "?" + data
    return new_url

def eth_addr_to_string(eth_addr):
    string_addr = eth_addr[2:]
    string_addr = string_addr.lower()
    return string_addr

def get_address_from_public_key_object(pub_key_string):
    pub_key = get_public_key(pub_key_string)
    return ECCipher.get_address_from_public_key(pub_key)

def get_public_key(public_key_string):
    pub_key_bytes = Encoder.hex_to_bytes(public_key_string)
    return ECCipher.create_public_key(pub_key_bytes)
