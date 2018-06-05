import hashlib
import logging
import random

from django.http import JsonResponse

from cpchain.crypto import ECCipher
from cpchain.utils import Encoder, SHA256Hash

logger = logging.getLogger(__name__)

PUBLIC_KEY = "public_key"
HTTP_MARKET_TOKEN = 'HTTP_MARKET_TOKEN'

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


def is_valid_signature(public_key_string, raw_data, signature):
    public_key_bytes = Encoder.hex_to_bytes(public_key_string)
    public_key = ECCipher.create_public_key(public_key_bytes)
    logger.debug(
        "is_valid_verify_code public_key:" + public_key_string + ",raw_data:" + raw_data + ",signature:" + signature)
    return verify_signature(public_key, signature, raw_data)


def generate_signature(pri_key_string, raw_data, password=None):
    return sign(pri_key_string=pri_key_string, raw_data=raw_data, password=password)


def generate_market_hash(msg_hash_source):
    return SHA256Hash.generate_hash(msg_hash_source)


def verify_signature(public_key, signature, raw_data_string):
    raw_data = raw_data_string.encode(encoding="utf-8")
    return ECCipher.verify_sign(public_key, signature, raw_data)


def sign(private_key, message):
    return ECCipher.create_signature(private_key=private_key, message=message)


def get_address_from_public_key_object(pub_key_string):
    pub_key = get_public_key(pub_key_string)
    return ECCipher.get_address_from_public_key(pub_key)


def get_public_key(public_key_string):
    pub_key_bytes = Encoder.hex_to_bytes(public_key_string)
    return ECCipher.create_public_key(pub_key_bytes)


def create_invalid_response(status=0, message="invalid request"):
    return JsonResponse({"status": status, "message": message})


def create_success_response():
    return JsonResponse({"status": 1, "message": "success"})


def create_success_data_response(data):
    return JsonResponse({"status": 1, "message": "success", "data": data})


def create_login_success_data_response(data):
    return JsonResponse({"status": 1, "message": data})


def get_header(request, head_name='HTTP_MARKET_KEY'):
    value = request.META.get(head_name, None)
    if value is None:
        another_head_name = get_short_name(head_name)
        value = request.META.get(another_head_name, None)

    return value


def get_short_name(head_name):
    names = head_name.split('_')
    if len(names) > 1:
        return "-".join(names[1:])
    return head_name


class ExceptionHandler(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, type=None):
        return self.__class__(self.func.__get__(obj, type))

    def __call__(self, *args, **kwargs):
        try:
            ret_val = self.func(*args, **kwargs)
        except:
            logger.exception("global exception handle in view:")
            return create_invalid_response()
        return ret_val
