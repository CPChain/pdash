from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from cpchain.utils import join_with_root
from cpchain import config

# Generate our key
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
    backend=default_backend()
    )

# Write our key to disk for safe keeping
with open(join_with_root(config.wallet.rsa_private_key_file), "wb") as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(b"cpchainisawesome"),
        ))

with open(join_with_root(config.wallet.rsa_private_key_password_file), "wb") as f:
    f.write(b"cpchainisawesome")
