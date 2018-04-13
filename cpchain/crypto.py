import base64
import os
import functools
import logging

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cpchain import config

from cpchain.chain.utils import load_private_key_from_keystore

logger = logging.getLogger(__name__)


def examine_password(password):
    password = password or config.market.default_password
    password_bytes = password.encode(encoding="utf-8")
    return password_bytes


class BaseCipher:
    def get_digest(self, fpath):
        digest = hashes.Hash(hashes.SHA256(), backend=self.backend)
        with open(fpath, 'rb') as f:
            for buffer in iter(functools.partial(f.read, 4096), b''):
                digest.update(buffer)
            d = digest.finalize()
        return d

    def is_valid(self, fpath, d):
        digest = hashes.Hash(hashes.SHA256(), backend=self.backend)
        with open(fpath, 'rb') as f:
            for buffer in iter(functools.partial(f.read, 4096), b''):
                digest.update(buffer)

            return d == digest.finalize()


class AESCipher(BaseCipher):
    def __init__(self, key: '128bit aes-key'):
        self.backend = default_backend()
        self.key = key

    @staticmethod
    def generate_key():
        return os.urandom(16)

    def encrypt(self, fpath, outpath):
        with open(fpath, "rb") as infile, open(outpath, "wb") as outfile:
            # NB the same length as aes
            iv = os.urandom(16)
            # we write the iv to the outfile
            outfile.write(iv)
            encryptor = Cipher(algorithms.AES(self.key), modes.CFB(iv), self.backend).encryptor()

            for buffer in iter(functools.partial(infile.read, 4096), b''):
                cipherdata = encryptor.update(buffer)
                outfile.write(cipherdata)

            cipherdata = encryptor.finalize()
            outfile.write(cipherdata)

    def decrypt(self, fpath, outpath):
        with open(fpath, 'rb') as infile, open(outpath, 'wb') as outfile:
            iv = infile.read(16)
            decryptor = Cipher(algorithms.AES(self.key), modes.CFB(iv), self.backend).decryptor()

            for buffer in iter(functools.partial(infile.read, 4096), b''):
                data = decryptor.update(buffer)
                outfile.write(data)

            data = decryptor.finalize()
            outfile.write(data)


class ECCipher:
    # cf. yellow paper
    # cf. http://tinyurl.com/y8q5g68u
    @staticmethod
    def geth_load_key_pair_from_private_key(fpath, password='password'):
        pri_key_bytes = load_private_key_from_keystore(fpath, password)

        pri_key_string = Encoder.bytes_to_base64_str(pri_key_bytes)

        pub_key_string = ECCipher._get_public_key_from_private_key_string(pri_key_bytes)

        return pri_key_string, pub_key_string

    @staticmethod
    def geth_get_public_key_from_private_key(pri_key_string):

        key_bytes = Encoder.str_to_base64_byte(pri_key_string)

        return ECCipher._get_public_key_from_private_key_string(key_bytes)

    @staticmethod
    def _get_key_pairs_from_private_key_bytes(private_key_bytes):
        private_key = ECCipher._load_private_key_from_bytes(private_key_bytes)
        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_key_bytes, public_key_bytes

    @staticmethod
    def _get_public_key_from_private_key_string(private_key_bytes):
        private_key_bytes, pub_key_bytes = ECCipher._get_key_pairs_from_private_key_bytes(private_key_bytes)
        pub_key_string = Encoder.bytes_to_base64_str(pub_key_bytes)
        logger.debug("pub_key_string:%s" % pub_key_string)
        return pub_key_string

    @staticmethod
    def geth_sign(pri_key_string, raw_data):
        try:
            pri_key_string_bytes = Encoder.str_to_base64_byte(pri_key_string)

            private_key = ECCipher._load_private_key_from_bytes(pri_key_string_bytes)

            signature_string = private_key.sign(
                raw_data.encode(encoding="utf-8"),
                ec.ECDSA(hashes.SHA256()))
            return Encoder.bytes_to_base64_str(signature_string)
        except Exception:
            logger.exception("signature error")
            return None

    @staticmethod
    def _load_private_key_from_bytes(pri_key_string_bytes):
        # XXX big endian
        private_value = int.from_bytes(pri_key_string_bytes, byteorder='big')
        private_key = ec.derive_private_key(private_value, ec.SECP256K1(), default_backend())
        return private_key

    @staticmethod
    def generate_key_pair(private_key_bytes=None, password=None):
        password = examine_password(password)

        if private_key_bytes:
            serialized_private = private_key_bytes
            private_key = ECCipher._load_private_key_from_bytes(private_key_bytes)
            public_key = private_key.public_key()
            serialized_public = public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            logger.debug("pri key bytes:%s" % private_key_bytes)
            logger.debug("pub key bytes:%s" % serialized_public)

        else:
            private_key = ec.generate_private_key(
                ec.SECP256K1(),
                default_backend()
            )

            serialized_private = private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(password)
            )

        public_key = private_key.public_key()
        serialized_public = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return serialized_private, serialized_public

    @staticmethod
    def generate_signature(pri_key_string_bytes, raw_data, password=None):
        try:
            loaded_private_key = ECCipher._load_private_key_from_bytes(pri_key_string_bytes)
            # loaded_private_key = serialization.load_der_private_key(
            #     private_key,
            #     password=password,
            #     backend=default_backend()
            # )
            signature = loaded_private_key.sign(
                raw_data,
                ec.ECDSA(hashes.SHA256()))

        except Exception:
            logger.exception("generate signature error")
            return None
        else:
            return signature

    @staticmethod
    def verify_signature(public_key, signature, raw_data):
        try:
            loaded_public_key = serialization.load_der_public_key(
                public_key,
                backend=default_backend()
            )
            loaded_public_key.verify(
                signature,
                raw_data,
                ec.ECDSA(hashes.SHA256()))

        except Exception:
            logger.exception("verify signature error")
            return False
        else:
            return True

    @staticmethod
    def generate_der_keys(password=None):
        password = examine_password(password)
        private_key = ec.generate_private_key(
            ec.SECP256K1(), default_backend()
        )

        serialized_private = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )

        pri_key_string = Encoder.bytes_to_base64_str(serialized_private)
        logger.debug("pri_key_string:%s" % pri_key_string)
        puk = private_key.public_key()
        serialized_public = puk.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        pub_key_string = Encoder.bytes_to_base64_str(serialized_public)
        logger.debug("pub_key_string:%s" % pub_key_string)
        return pri_key_string, pub_key_string

    @staticmethod
    def verify_der_signature(pub_key_string, signature, raw_data_string):
        try:
            pub_key_string_bytes = Encoder.str_to_base64_byte(pub_key_string)
            loaded_public_key = serialization.load_der_public_key(
                pub_key_string_bytes,
                backend=default_backend()
            )
            loaded_public_key.verify(Encoder.str_to_base64_byte(signature), raw_data_string.encode(encoding="utf-8"),
                                     ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            logger.exception("verify signature error")
            return False

    @staticmethod
    def sign_der(pri_key_string, raw_data, password=None):
        try:
            password = examine_password(password)
            pri_key_string_bytes = Encoder.str_to_base64_byte(pri_key_string)
            loaded_private_key = serialization.load_der_private_key(
                pri_key_string_bytes,
                password=password,
                backend=default_backend()
            )
            signature_string = loaded_private_key.sign(
                raw_data.encode(encoding="utf-8"),
                ec.ECDSA(hashes.SHA256()))
            return Encoder.bytes_to_base64_str(signature_string)
        except Exception:
            logger.exception("signature error")
            return None

    @staticmethod
    def get_public_key_from_private_key(pri_key_string, password=None):
        """
        get public key from private key
        :param pri_key_string:
        :param password:read default value from config file
        :return:base64(public key)
        """
        password = examine_password(password)
        pri_key_string_bytes = Encoder.str_to_base64_byte(pri_key_string)

        loaded_private_key = serialization.load_der_private_key(
            pri_key_string_bytes,
            password=password,
            backend=default_backend()
        )
        puk = loaded_private_key.public_key()
        serialized_public = puk.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return Encoder.bytes_to_base64_str(serialized_public)


class ECPEMCipher:
    """
    PEM encoding EC
    """

    @staticmethod
    def generate_keys(password=None):
        password = examine_password(password)

        private_key = ec.generate_private_key(
            ec.SECP256K1(), default_backend()
        )

        serialized_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )

        private_key_list = []
        pis = serialized_private.splitlines()
        for p in pis:
            private_key_list.append(p.decode("utf-8"))
            private_key_list.append('\n')
        pri_key_string = ''.join(private_key_list)

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

    @staticmethod
    def verify_signature(pub_key_string, signature, raw_data):
        try:
            loaded_public_key = serialization.load_pem_public_key(
                pub_key_string,
                backend=default_backend()
            )
            loaded_public_key.verify(Encoder.str_to_base64_byte(signature), raw_data, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            logger.exception("verify signature error")
            return False

    @staticmethod
    def sign(pri_key_string, raw_data, password=None):
        try:
            password = examine_password(password)
            loaded_private_key = serialization.load_pem_private_key(
                pri_key_string,
                password=password,
                backend=default_backend()
            )
            signature_string = loaded_private_key.sign(
                raw_data,
                ec.ECDSA(hashes.SHA256()))
            return Encoder.bytes_to_base64_str(signature_string)
        except Exception:
            logger.exception("pem sign error")
            return None


class RSACipher:
    def __init__(self, priv_bytes, pub_bytes):
        self.backend = default_backend()
        self.priv_key = serialization.load_pem_private_key(priv_bytes,
                                                           password=None,
                                                           backend=self.backend)
        self.pub_key = serialization.load_pem_public_key(pub_bytes,
                                                         backend=self.backend)

    @staticmethod
    def generate_private_key() -> "returns key bytes":
        priv_key = rsa.generate_private_key(public_exponent=65537,
                                            key_size=4096,
                                            backend=default_backend())

        pub_key = priv_key.public_key()

        priv_bytes = priv_key.private_bytes(encoding=serialization.Encoding.PEM,
                                            format=serialization.PrivateFormat.TraditionalOpenSSL,
                                            encryption_algorithm=serialization.NoEncryption())

        pub_bytes = pub_key.public_bytes(encoding=serialization.Encoding.PEM,
                                         format=serialization.PublicFormat.SubjectPublicKeyInfo)

        return priv_bytes, pub_bytes


class SHA256Hash:

    @staticmethod
    def generate_hash(data):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data.encode(encoding="utf-8"))
        digest_data = digest.finalize()
        digest_string = Encoder.bytes_to_base64_str(digest_data)
        return digest_string


class Encoder:
    @staticmethod
    def bytes_to_base64_str(b64bytes):
        return base64.b64encode(b64bytes).decode("utf-8")

    @staticmethod
    def str_to_base64_byte(b64string):
        return base64.b64decode(b64string.encode("utf-8"))
