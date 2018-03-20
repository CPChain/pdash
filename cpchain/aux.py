import os.path as osp
import toml

root_dir = osp.abspath(osp.join(osp.dirname(osp.abspath(__file__)), '../'))

config = toml.load(osp.join(root_dir, 'cpchain/cpchain.toml'))
