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
    # return ECCipher.generate_keys()
    return ECCipher.generate_der_keys()


def verify_signature(pub_key_string, signature, raw_data):
    return ECCipher.verify_der_signature(pub_key_string=pub_key_string, signature=signature, raw_data_string=raw_data)


def sign(pri_key_string, raw_data):
    return ECCipher.sign_der(pri_key_string, raw_data)


if __name__ == '__main__':
#     test_private_key_string = '''-----BEGIN ENCRYPTED PRIVATE KEY-----
# MIHsMFcGCSqGSIb3DQEFDTBKMCkGCSqGSIb3DQEFDDAcBAjzToaLuvPQzwICCAAw
# DAYIKoZIhvcNAgkFADAdBglghkgBZQMEASoEEOZ1gvi979iOQ0tEAG34vVoEgZA1
# FUgBPISB9LpKJECvQ5Vu6ftYWRiIlg8JOQbP45VdlaeHqNSFhieq3L8G+NaXtLKN
# GZpWE+Y/yKRMI1+fDu4Z/OAOCPiwjaoaNA3bRx740Gi3HD7PcD7viv3fMwHG0FgU
# sT8i5fYH4n7jzD4FS1/+c7SkwH/eLdTvYGmX+uzCOMJ8VGntnq1xR3LigXAnXrg=
# -----END ENCRYPTED PRIVATE KEY-----'''.encode(encoding="utf-8")
#
#     test_public_key = '''-----BEGIN PUBLIC KEY-----
# MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEFTgSuaPEkOfJicDM0+Y2fZw2lbQEebFp
# erZxolqxK6hu+9jKTfXtImfn5R5flHjzkA0NTHohdXZIE9prp8C9bQ==
# -----END PUBLIC KEY-----'''.encode(encoding="utf-8")
#
#     expected_signature = "3044022057399397A98750206F9E2CCCD341C86A6BD917A7EAB16F385ED45F8E2E181FE3022044C0C7545A808182E1CBDBF1E4477A6BFD617F4130B3AE12F0919B51B5274660"
#     print("test_private_key_string:")
#     print(test_private_key_string)
#     print("test_public_key:")
#     print(test_public_key)
#     print("expected_signature:")
#     print(expected_signature)
#
#     print("\n========= start sign =========")
#     sample = "hello".encode(encoding="utf-8")
#
#     print("sample string:")
#     print(sample)
#
#     test_signature = sign(test_private_key_string, sample)
#     print("test_signature is:")
#     print(test_signature)
#
#     is_valid_sign = verify_signature(test_public_key, test_signature, sample)
#     print("verify signature:" + str(is_valid_sign))
#
#     print("================generate keys=================")
#     private_key_string, public_key_string = generate_keys()
#     print("pri key:\n", private_key_string)
#     print("pub key:\n", public_key_string)
#     new_signature = sign(private_key_string.encode(encoding="utf-8"), sample)
#     print("new_signature is:")
#     print(new_signature)
#
#     is_valid_sign = verify_signature(public_key_string.encode(encoding="utf-8"), new_signature, sample)
#     print("is valid new_signature:" + str(is_valid_sign))
#
#     sha256("hello")


    sample = "3056301006072A8648CE3D020106052B8104000A034200041A3485E29B89CA3005C4A7472DC19E84F0D75E85CF8B3228FA0BA79507E8ECE6AF6A9536FAC94C33575A97F88B802022EC4064A92850F34A3DA1BDBBE304B159666('667788',)(1224,)2018-04-01 10:10:102018-04-01 10:10:101234567890"
    private_key_string, public_key_string = generate_keys()

    print("pri key:"+private_key_string)
    print("pub key:"+public_key_string)


    new_signature = sign(private_key_string, sample)
    print("new_signature is:")
    print(new_signature)

    is_valid_sign = verify_signature(public_key_string, new_signature, sample)
    print("is valid new_signature:" + str(is_valid_sign))


    private_key_string = "3081EC305706092A864886F70D01050D304A302906092A864886F70D01050C301C0408BFE08D732DD166F502020800300C06082A864886F70D02090500301D060960864801650304012A041021C71C4F400AED4F63179E57B72249C004819025903D13D36E7BBE786ACF97535FD89ECAE09323657E7BFF3D3CF2F37047FE9E4D8A2F0A83DE1431332BB28F9B271785C31294B631E50CF1D2925BF0DA61A15509D90B415AD55381F440EBC6C73DCA64316A6B18C57A6B368141329BDA5D09EF645B9AD9366ECCDE15B816FE4C8FFF277D4DDF52DB1737C1EC8B1750EBD1C25274E17F37B060DCFA77ECDBD9D4B89AAD"
    data = "qZaQ6S"

    print(sign(private_key_string,data))

    data = "3056301006072A8648CE3D020106052B8104000A034200041A3485E29B89CA3005C4A7472DC19E84F0D75E85CF8B3228FA0BA79507E8ECE6AF6A9536FAC94C33575A97F88B802022EC4064A92850F34A3DA1BDBBE304B159666('667788',)(1224,)2018-04-01 10:10:102018-04-01 10:10:101234567890"
    print(sign(private_key_string, data))
