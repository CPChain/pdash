import hashlib
import random
import logging

logger = logging.getLogger(__name__)


def md5(source):
    digest = hashlib.md5()
    digest.update(source)
    return digest.hexdigest()


def generate_random_str(randomlength=16):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def is_valid_signature(public_key, verify_code, signature):
    # TODO verify signature of public_key+verify_code
    print("is_valid_verify_code public_key:" + public_key + ",verify_code:" + verify_code + ",signature:" + signature)
    return md5("".join([public_key,verify_code]).encode("utf-8")) == signature


def generate_signature(signature_source):
    # TODO replace me!
    return md5(signature_source)


def generate_msg_hash(msg_hash_source):
    # TODO replace me!
    return md5(msg_hash_source)
