from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from cpchain.encoder import Encoder


class SHA256Hash:

    @staticmethod
    def generate_hash(data):
        """
        generate hash code like this : base64(sha256(data))

        Args:
            data: str data

        Returns:
            base64 str

        """
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data.encode(encoding="utf-8"))
        digest_data = digest.finalize()
        digest_string = Encoder.bytes_to_base64_str(digest_data)
        return digest_string

