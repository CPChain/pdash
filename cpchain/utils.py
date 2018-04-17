import os.path as osp
import sys
import subprocess

import logging
import toml

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


config = Config(toml.load(osp.join(root_dir, 'cpchain/cpchain.toml')))


# logging
logging.basicConfig(format="%(levelname)s:%(module)s:%(funcName)s:L%(lineno)d:%(message)s", level=logging.DEBUG)


def join_with_root(path):
    return osp.join(root_dir, path)


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
