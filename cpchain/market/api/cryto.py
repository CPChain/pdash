import logging

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature, encode_dss_signature

logger = logging.getLogger(__name__)


def test(signature_source):

    # TODO replace me!
    # data = b"this is some data I'd like to sign"
    data = signature_source.encode(encoding="utf-8")
    print(type(data))
    private_key = ec.generate_private_key(
        ec.SECP384R1(), default_backend()
    )

    serialized_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(b'testpassword11')
        # encryption_algorithm=serialization.NoEncryption
    )
    print("private key:")
    pls=serialized_private.splitlines()
    for p in pls:
        print(p.decode("utf-8"))

    signature = private_key.sign(
        data, ec.ECDSA(hashes.SHA256()))
    print("hex sign:" + ByteToHex(signature))
    print("type signature:" + str(type(signature)))
    # print("signature:" + signature.decode("utf-8"))
    print("signstr:" + str(signature))

    dd = decode_dss_signature(signature)
    print(type(dd))
    print("sign:" + str(dd))


    # print(dd[0])
    # print(dd[1])
    ss = encode_dss_signature(r=dd[0], s=dd[1])
    print(type(ss))


    public_key = private_key.public_key()
    serialized_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    print(type(serialized_public))
    pp = serialized_public.splitlines()
    print("public key:")
    for p in pp:
        print(p.decode("utf-8"))

    # dd1,dd2 = dd
    # e_sign = encode_dss_signature(dd1,dd2)
    # print("e_sign:" + str(e_sign))

    # public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))

    print("===========================================")
    try:
        public_key.verify(ss, data, ec.ECDSA(hashes.SHA256()))
        print("y")
    except:
        print("x")


def verify_signature_with_serialized_public_key():
    data = "dsfdsfdsf".encode(encoding="utf-8")
    public_key = '''-----BEGIN PUBLIC KEY-----
MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEsbkIAbySOPxibjkWqQfFf+fqogSOlLWb
SciZdNJgzjyyuINqyPm0BvsWpV866HTIYMYuD5ZZSOBAeVzs25q6FmIl7OVOS9fT
Q35TpG0FghR3T0XTwj6IfbCJacMS/egd
-----END PUBLIC KEY-----'''.encode(encoding="utf-8")

    loaded_public_key = serialization.load_pem_public_key(
        public_key,
        backend = default_backend()
    )
    print("loaded_public_key:")
    print(loaded_public_key)
    hex = "3064023066FF18EB8B6EA2DEA804E2DB1D7B640D4EC2E2F8B04E79A5E3CFB3A606FC94D5A7C95EAA13114B546B0A93ADBCAB5EC402301E571612B3B139E00B9255F065E1A3E8D0F9B837D585D061AB69A5572B34F3164A93944CB339D7A7854DE6410296149C"
    hexSign = HexToByte(hex)
    loaded_public_key.verify(hexSign, data, ec.ECDSA(hashes.SHA256()))

    private_key ='''-----BEGIN ENCRYPTED PRIVATE KEY-----
MIIBHDBXBgkqhkiG9w0BBQ0wSjApBgkqhkiG9w0BBQwwHAQIym4J0AldqFoCAggA
MAwGCCqGSIb3DQIJBQAwHQYJYIZIAWUDBAEqBBA3Y6UDkUA+YB0EyuJkd/aqBIHA
0L8SbnxJYhAoRrfTTghTN3LLHMm6HXGmXHvSrWpDx3Lpz/Tt75SM4kPij+8Go1hz
zTvjJsVtqjzrAoAN064pyVpuhaXOnHkhgVOMfzqnEcv42a88NoNzBZseil6vP/Rd
o0dmj9HJQ+I2PRnECOTDtcQMx2tb5O1kYhwUZPOVcOwsUvlkhUBiD/RtEa20xXPS
0azgmCReVBcCrhgOnbbM73vdjLeThJ3089blgqfTIAJHtc18vUqJOOqvbRdpVDVF
-----END ENCRYPTED PRIVATE KEY-----'''
    loaded_private_key = serialization.load_pem_private_key(
        private_key,
        backend=default_backend()
    )

    return True


def ByteToHex(bins):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """
    return ''.join(["%02X" % x for x in bins]).strip()


def HexToByte(hexStr):
    """
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    """
    return bytes.fromhex(hexStr)

if __name__ == '__main__':

    test("dsfdsfdsf")
    print("----------------------------------------------")
    verify_signature_with_serialized_public_key()


