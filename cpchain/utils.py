import base64
import os
import os.path as osp
import sys
import subprocess

import toml
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

root_dir = osp.abspath(osp.join(osp.dirname(osp.abspath(__file__)), '../'))

class Config:
    def __init__(self, conf):
        self.conf = conf

    def __getattr__(self, name):
        # twisted trial will query some non-existing attrs.
        if name not in self.conf:
            return

        if not isinstance(self.conf[name], dict):
            return self.conf[name]
        return Config(self.conf[name])

    def __getitem__(self, key):
        return self.conf[key]


def _get_config():
    def merge_dict(d, d2):
        for k in d2.keys():
            if k in d and isinstance(d[k], dict) and isinstance(d2[k], dict):
                merge_dict(d[k], d2[k])
            else:
                d[k] = d2[k]

    conf = toml.load(osp.join(root_dir, 'cpchain/cpchain.toml'))
    config_file = os.getenv("CPCHAIN_HOME_CONFIG_PATH", "~/.cpchain/cpchain.toml")
    print('config file path:', config_file)
    user_path = osp.expanduser(config_file)
    if osp.exists(user_path):
        merge_dict(conf, toml.load(user_path))

    return Config(conf)


config = _get_config()


# twisted reactor
def _install_reactor():
    reactor_qual_name = "twisted.internet.reactor"
    if reactor_qual_name not in sys.modules:
        if config.core.mode == "proxy":
            import asyncio
            from twisted.internet import asyncioreactor
            loop = asyncio.get_event_loop()
            asyncioreactor.install(eventloop=loop)
        elif config.core.mode == "wallet":
            # TODO, add qmuash support
            import asyncio
            import time
            from PyQt5.QtWidgets import QApplication, QProgressBar
            from quamash import QEventLoop, QThreadExecutor
            app = QApplication(sys.argv)
            loop = QEventLoop(app)
            asyncio.set_event_loop(loop)
            from twisted.internet import asyncioreactor
            asyncioreactor.install(eventloop=loop)
            from twisted.internet import reactor

    return sys.modules.get(reactor_qual_name)

reactor = _install_reactor()


def join_with_root(path):
    return osp.join(root_dir, path)


rc_dir = osp.expanduser(config.core.rc_dir)

def join_with_rc(path):
    return osp.join(rc_dir, path)


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def open_file(path):
    executable = dict(linux='xdg-open',
                      darwin='open')

    subprocess.call((executable[sys.platform], path))


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

    @staticmethod
    def bytes_to_hex(hex_bytes):
        return hex_bytes.hex()

    @staticmethod
    def hex_to_bytes(hex_string):
        try:
            return bytes.fromhex(hex_string)
        except:
            return None


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
