import os.path as osp
import subprocess

import cpchain
from cpchain.crypto import RSACipher
from cryptography.hazmat.primitives import hashes, serialization

priv_key =  RSACipher.generate_private_key(password=b'cpchainisawesome')


pub_key = priv_key.public_key()

pub_bytes = pub_key.public_bytes(encoding=serialization.Encoding.DER,
                                 format=serialization.PublicFormat.SubjectPublicKeyInfo)

print(len(pub_bytes))