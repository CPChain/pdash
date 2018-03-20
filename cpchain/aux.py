import os.path as osp

root_dir = osp.abspath(osp.join(osp.dirname(osp.abspath(__file__)), '../'))


import toml

config = toml.load(osp.join(root_dir, 'cpchain/cpchain.toml'))
