import glob
import os
import os.path as osp
import json
from datetime import datetime
from eth_account import Account as eth_account

from cpchain import config, crypto
from cpchain.utils import join_with_rc

_keystore_dir = join_with_rc(config.account.keystore_dir)
os.makedirs(_keystore_dir, exist_ok=True)

class Accounts(list):
    def __init__(self, *args):
        super().__init__(*args)
        self.default_account = None
        self._populate_accounts()

    def _populate_accounts(self):
        ptn = osp.join(_keystore_dir, 'UTC-*')

        # TODO for now, we use the password stored in the file

        key_passphrase = open(osp.join(_keystore_dir, 'password')).read()
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


def create_account(passwd):

    acct = eth_account.create()

    # follow eth keystore naming rule
    # go-ethereum/accounts/keystore/key.go:208
    # // keyFileName implements the naming convention for keyfiles:
    # // UTC--<created_at UTC ISO8601>-<address hex>
    # func keyFileName(keyAddr common.Address) string {
    #     ts := time.Now().UTC()
    #     return fmt.Sprintf("UTC--%s--%s", toISO8601(ts), hex.EncodeToString(keyAddr[:]))
    # }

    key_file = osp.join(
        _keystore_dir,
        "UTC--%s--%s" % (datetime.utcnow().isoformat(), acct.address[2:].lower())
    )
    encrypted_key = eth_account.encrypt(acct.privateKey, passwd)

    with open(key_file, 'w') as f:
        f.write(json.dumps(encrypted_key))

    return Account(key_file, passwd.encode('utf8'))
