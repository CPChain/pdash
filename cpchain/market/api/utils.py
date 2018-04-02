import hashlib
import random


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


def encrypte_verify_code(public_key, code):
    """

    :param public_key:
    :param code:
    :return:
    """
    return code


def is_valid_verify_code(public_key, verify_code):
    return True
