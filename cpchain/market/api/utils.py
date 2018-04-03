import hashlib
import logging
import random

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

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
    return md5("".join([public_key, verify_code]).encode("utf-8")) == signature


def generate_signature(signature_source):
    # TODO replace me!
    return md5(signature_source)


def generate_msg_hash(msg_hash_source):
    # TODO replace me!
    return md5(msg_hash_source)


def generate_keys():
    # SECP384R1,SECP256R1
    private_key = ec.generate_private_key(
        ec.SECP384R1(), default_backend()
    )

    serialized_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        # encryption_algorithm=serialization.NoEncryption
        encryption_algorithm=serialization.BestAvailableEncryption(b'testpassword11')
    )

    private_key_list = []
    pis = serialized_private.splitlines()
    for p in pis:
        private_key_list.append(p.decode("utf-8"))
        private_key_list.append('\n')
    pri_key_string = ''.join(private_key_list)
    # print("private key:\n" + pri_key_string)

    public_key_list = []
    puk = private_key.public_key()
    serialized_public = puk.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    pus = serialized_public.splitlines()
    for p in pus:
        public_key_list.append(p.decode("utf-8"))
        public_key_list.append('\n')

    pub_key_string = ''.join(public_key_list)
    return pri_key_string, pub_key_string


def verify_signature(pub_key_string, signature, raw_data):
    try:
        loaded_public_key = serialization.load_pem_public_key(
            pub_key_string,
            backend=default_backend()
        )
        loaded_public_key.verify(hex_to_byte(signature), raw_data, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False


def sign(pri_key_string, raw_data):
    try:
        loaded_private_key = serialization.load_pem_private_key(
            pri_key_string,
            backend=default_backend()
        )
        signature = loaded_private_key.sign(
            raw_data, ec.ECDSA(hashes.SHA256()))
        print("hex sign:" + byte_to_hex(signature))

        to_hex = byte_to_hex(signature)
        return to_hex
    except Exception:
        print("error")
        return None


def byte_to_hex(hex_bytes):
    return ''.join(["%02X" % x for x in hex_bytes]).strip()


def hex_to_byte(hex_string):
    return bytes.fromhex(hex_string)


if __name__ == '__main__':
    private_key_string, public_key_string = generate_keys()
    print("pri key:%r", private_key_string)
    print("pub key:%r", public_key_string)

    private_key_string = '''-----BEGIN ENCRYPTED PRIVATE KEY-----
MIIBHDBXBgkqhkiG9w0BBQ0wSjApBgkqhkiG9w0BBQwwHAQIGXjZc/lY2fICAggA
MAwGCCqGSIb3DQIJBQAwHQYJYIZIAWUDBAEqBBCkoLS2yLTnddr+1P3DJz02BIHA
KsNPNwSuQcc9fueSqqcJf9ZL8yweIEKXsqN0j+u1DPdBPFipcY1eMSMYs5NbiO8r
MLRrpVZWhLvm6TkMxpaKuLoOGdduUZBhJ6ZME+KC0ntW2/sPxhh+g48E/xOlGWnZ
jp9bAqDz5fRAguKW5hUugLHij0qlzrowZkY4YlpY951PyCIgOxTT0KAuxqc06uGe
eIPNUIpOMC1gePIL/pzGnOMmJrBmDU0gCeOBSHixrMHpTuhUTjsUIlXHpYFjKn9K
-----END ENCRYPTED PRIVATE KEY-----'''

    signature = sign(private_key_string, "hello")
    print(signature)
    is_valid_sign = verify_signature(public_key_string,signature,"hello")
    print("is valid signature:" + str(is_valid_sign))

    data = "dsfdsfdsf".encode(encoding="utf-8")
    hex = "306402307F6782A9FF09D8DBCE78925C0AE140813A3E35427CF27040302AB6D6E42719657BDD3FC6727E1EAF1C4BC77EE1EF5D0002307F58AEE673623AA73312B8BC64AAC9469F7A5891AD998EF44ADD98DCF23CF1F87B92B185F357C072F11AD1A8C5210C40"
    public_key = '''-----BEGIN PUBLIC KEY-----
MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEIQxH3M3v6r+db0IJvAK1H0zl5EIZxYUD
Nt55TAF7TbgEgz4Ocj5HexsjY0R7jsxC5fjmWTEbwF7zUYEj9l0REksK19Ubl7aN
ap81GPcZp2bqzGubL7mv0CwoQaDf7XLD
-----END PUBLIC KEY-----'''.encode(encoding="utf-8")

    logger.info("is valid:%r", verify_signature(pub_key_string=public_key, signature=hex, raw_data=data))
