import os.path as osp
import toml

root_dir = osp.abspath(osp.join(osp.dirname(osp.abspath(__file__)), '../'))


class Config:
    def __init__(self, conf):
        self.conf = conf

    def __getattr__(self, name):
        if not isinstance(self.conf[name], dict):
            return self.conf[name]
        return Config(self.conf[name])

    def __getitem__(self, key):
        return self.conf[key]

config = Config(toml.load(osp.join(root_dir, 'cpchain/cpchain.toml')))
