import os.path as osp
import subprocess

import cpchain
from cpchain.crypto import AESCipher


key = b'\xaf\x1a8\x9f_=\xac\xb5"$.\xd2\xcb\xdf\xfb\xeb'


cipher = AESCipher(key)

fpath = osp.join(cpchain.root_dir, "tools/assets/shakespeare.txt")
outpath = osp.join(cpchain.root_dir, "tools/crypto/_local_en-sp.txt")

cipher.encrypt(fpath, outpath)

d = cipher.get_digest(outpath)
print("valid" if cipher.is_valid(outpath, d) else "invalid")

newpath = osp.join(cpchain.root_dir, "tools/crypto/_local_de-sp.txt")

cipher.decrypt(outpath, newpath)

subprocess.run(['sha256sum', fpath])
subprocess.run(['sha256sum', newpath])
