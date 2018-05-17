import glob
import os.path as osp

from cpchain import config, crypto
from cpchain.utils import join_with_root

class Accounts(list):
    def __init__(self, *args):
        super().__init__(*args)
        self.default_account = None
        self._populate_accounts()

    def _populate_accounts(self):
        key_dir = join_with_root(config.account.keystore_dir)
        ptn = osp.join(key_dir, 'UTC-*')
        
        # TODO for now, we use the password stored in the file
        key_passphrase = open(osp.join(key_dir, 'password')).read()
        for key_path in glob.glob(ptn):
            account = Account(key_path, key_passphrase)
            self.append(account)

        if len(self):
            self.default_account = self[0]

    def set_default_account(self, idx):
        assert idx < len(self)
        self.default_account = self[idx]


class Account:
    def __init__(self, key_path, key_passphrase=None):
        if not key_passphrase:
            key_passphrase = input("Input Key Passphrase: ")
        self.private_key, self.public_key = crypto.ECCipher.load_key_pair(key_path, key_passphrase)

if __name__ == '__main__':
    accounts = Accounts()
