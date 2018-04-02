import os
import functools

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import ec, rsa


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
    def __init__(self, key:'128bit aes-key'):
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
    # NB we shall use ec for signature only.  using ecies is too contrived.
    def __init__(self, priv_key:'ec secp256k1'):
        self.priv_key = key
        self.backend = default_backend()
        self.ecdsa = ec.ECDSA(hashes.SHA256())

    @staticmethod
    def generate_private_key():
        return ec.generate_private_key(ec.SECP256K1(), default_backend())

    @staticmethod
    def get_public_key(data):
        return serialization.load_der_public_key(data, backend=default_backend())


    def sign(self, data):
        return self.priv_key.sign(data, self.ecdsa)




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


    def encrypt(self, fpath, outpath):

        ciphertext = self.public_key.encrypt(
            text,
            self._get_padding()
        )
        if use_base64 is True:
            ciphertext = base64.b64encode(ciphertext)
        return ciphertext

        with open(fpath, "rb") as infile, open(outpath, "wb") as outfile:

            cipherdata = self.pub_key.encrypt(infile.read(),
                                              padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),
                                                           algorithm=hashes.SHA1(),
                                                           label=None))
            outfile.write(cipherdata)
                

    def decrypt(self, fpath, outpath):
        with open(fpath, 'rb') as infile, open(outpath, 'wb') as outfile:
            data = self.priv_key.decrypt(infile.read(),
                                         padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()),
                                                      algorithm=hashes.SHA1(),
                                                      label=None))
            outfile.write(data)
