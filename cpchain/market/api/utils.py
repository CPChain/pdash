import hashlib
import logging
import random
import traceback

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from cpchain.crypto import SHA256HashCipher,ECCipher

logger = logging.getLogger(__name__)

def md5(source):
    digest = hashlib.md5()
    digest.update(source)
    return digest.hexdigest()

def sha256(s):
    digest_string = SHA256HashCipher.generate_hash(s)
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
    print("is_valid_verify_code public_key:" + public_key + ",raw_data:" + raw_data + ",signature:" + signature)
    return verify_signature(public_key, signature, raw_data)


def generate_signature(pri_key_string,raw_data,password=None):
    return sign(pri_key_string=pri_key_string, raw_data=raw_data,password=password)

def generate_msg_hash(msg_hash_source):
    return SHA256HashCipher.generate_hash(msg_hash_source)


def generate_keys():
    return ECCipher.generate_keys()


def verify_signature(pub_key_string, signature, raw_data):
    return ECCipher.verify_signature(pub_key_string=pub_key_string, signature=signature, raw_data=raw_data)


def sign(pri_key_string, raw_data):
    return ECCipher.sign(pri_key_string, raw_data)


if __name__ == '__main__':
    test_private_key_string = '''-----BEGIN ENCRYPTED PRIVATE KEY-----
MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAjzToaLuvPQzwICCAAw
DAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEOZ1gvi979iOQ0tEAG34vVoEgZA1
FUgBPISB9LpKJECvQ5Vu6ftYWRiIlg8JOQbP45VdlaeHqNSFhieq3L8G+NaXtLKN
GZpWE+Y/yKRMI1+fDu4Z/OAOCPiwjaoaNA3bRx740Gi3HD7PcD7viv3fMwHG0FgU
sT8i5fYH4n7jzD4FS1/+c7SkwH/eLdTvYGmX+uzCOMJ8VGntnq1xR3LigXAnXrg=
-----END ENCRYPTED PRIVATE KEY-----'''.encode(encoding="utf-8")

    test_public_key = '''-----BEGIN PUBLIC KEY-----
MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEFTgSuaPEkOfJicDM0+Y2fZw2lbQEebFp
erZxolqxK6hu+9jKTfXtImfn5R5flHjzkA0NTHohdXZIE9prp8C9bQ==
-----END PUBLIC KEY-----'''.encode(encoding="utf-8")

    expected_signature = "3044022057399397A98750206F9E2CCCD341C86A6BD917A7EAB16F385ED45F8E2E181FE3022044C0C7545A808182E1CBDBF1E4477A6BFD617F4130B3AE12F0919B51B5274660"
    print("test_private_key_string:")
    print(test_private_key_string)
    print("test_public_key:")
    print(test_public_key)
    print("expected_signature:")
    print(expected_signature)

    print("\n========= start sign =========")
    sample = "hello".encode(encoding="utf-8")

    print("sample string:")
    print(sample)

    test_signature = sign(test_private_key_string, sample)
    print("test_signature is:")
    print(test_signature)

    is_valid_sign = verify_signature(test_public_key, test_signature, sample)
    print("verify signature:" + str(is_valid_sign))

    print("================generate keys=================")
    private_key_string, public_key_string = generate_keys()
    print("pri key:\n", private_key_string)
    print("pub key:\n", public_key_string)
    new_signature = sign(private_key_string.encode(encoding="utf-8"), sample)
    print("new_signature is:")
    print(new_signature)

    is_valid_sign = verify_signature(public_key_string.encode(encoding="utf-8"), new_signature, sample)
    print("is valid new_signature:" + str(is_valid_sign))

    sha256("hello")

