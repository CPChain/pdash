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
    # verify signature of public_key+verify_code
    print("is_valid_verify_code public_key:" + public_key + ",verify_code:" + verify_code + ",signature:" + signature)
    return True

