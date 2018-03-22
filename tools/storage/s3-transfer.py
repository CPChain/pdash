import os.path as osp
import cpchain
from cpchain.storage import S3Storage


storage = S3Storage()

storage.upload_file(osp.join(cpchain.root_dir, "tools/assets/shakespeare.txt"), "sp")

storage.download_file(osp.join(cpchain.root_dir, "tools/storage/_local_shakespeare.txt"), "sp", fsize=5300)
