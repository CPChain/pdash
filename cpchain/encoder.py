import base64


class Encoder:
    @staticmethod
    def bytes_to_base64_str(b64bytes):
        """
        convert bytes to base64 string
        Args:
            b64bytes:

        Returns: string

        """
        return base64.b64encode(b64bytes).decode("utf-8")

    @staticmethod
    def str_to_base64_byte(b64string):
        """
        convert base64 string to bytes
        Args:
            b64string:

        Returns: bytes

        """
        return base64.b64decode(b64string.encode("utf-8"))
