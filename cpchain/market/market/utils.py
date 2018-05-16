import hashlib
import logging
import random

from cpchain.crypto import ECCipher
from cpchain.utils import Encoder, SHA256Hash

logger = logging.getLogger(__name__)


def md5(source):
    digest = hashlib.md5()
    digest.update(source)
    return digest.hexdigest()


def sha256(s):
    digest_string = SHA256Hash.generate_hash(s)
    print(digest_string)
    return digest_string


def generate_random_str(randomlength=16):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def is_valid_signature(public_key, raw_data, signature):
    # TODO verify signature of public_key+verify_code
    logger.debug("is_valid_verify_code public_key:" + public_key + ",raw_data:" + raw_data + ",signature:" + signature)
    return verify_signature(public_key, signature, raw_data)


def generate_signature(pri_key_string, raw_data, password=None):
    return sign(pri_key_string=pri_key_string, raw_data=raw_data, password=password)


def generate_msg_hash(msg_hash_source):
    return SHA256Hash.generate_hash(msg_hash_source)


def verify_signature(pub_key_string, signature, raw_data_string):
    pub_key_string_bytes = Encoder.str_to_base64_byte(pub_key_string)
    signature_bytes = Encoder.str_to_base64_byte(signature)
    raw_data = raw_data_string.encode(encoding="utf-8")
    return ECCipher.verify_signature(pub_key_string_bytes, signature_bytes, raw_data)


def sign(pri_key_string, raw_data):
    return ECCipher.generate_string_signature(pri_key_string, raw_data)


def get_addr_from_public_key(public_key_string):
    pub_key_bytes = Encoder.str_to_base64_byte(public_key_string)
    pub_key_loaded = get_addr_from_public_key(pub_key_bytes)
    return get_addr_from_public_key(pub_key_loaded)
