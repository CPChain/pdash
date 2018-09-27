import glob
import os
import os.path as osp
import json
import logging

from datetime import datetime
from getpass import getpass

from cpchain import config, crypto
from cpchain.utils import join_with_rc
from cpchain.chain.utils import default_w3 as web3

logger = logging.getLogger(__name__)

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

    acct = web3.eth.account.create()

    try:
        web3.personal.importRawKey(acct.privateKey, passwd)
    except:
        logger.info("account already in node's keychain")

    web3.personal.unlockAccount(acct.address, passwd)

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
    encrypted_key = web3.eth.account.encrypt(acct.privateKey, passwd)

    with open(key_file, 'w') as f:
        f.write(json.dumps(encrypted_key))

    return Account(key_file, passwd.encode('utf8'))

def import_account(key_file, passwd):

    with open(key_file) as f:
        encrypted_key = json.load(f)

    private_key = web3.eth.account.decrypt(encrypted_key, passwd)
    acct = web3.eth.account.privateKeyToAccount(private_key)

    try:
        web3.personal.importRawKey(acct.privateKey, passwd)
    except:
        logger.info("account already in node's keychain")

    web3.personal.unlockAccount(acct.address, passwd)

    return Account(key_file, passwd.encode('utf8'))

def get_keystore_list():
    ptn = osp.join(_keystore_dir, 'UTC-*')
    return glob.glob(ptn)

def new_passwd():
    i = 3

    while i:
        i -= 1
        passwd = getpass('new key passphrase: ')
        confirm = getpass('retype key passphrase: ')

        if passwd == confirm:
            return passwd
        else:
            logger.info('passphrases do not match')

    raise Exception('passphrases not match more than 3 times')

def set_default_account():
    keystore_list = get_keystore_list()

    if keystore_list:
        keystore_file = keystore_list[0]
        logger.info('import eth account from %s' % os.path.basename(keystore_file))
        passwd = getpass('enter key passphrase: ')
        account = import_account(keystore_file, passwd)
    else:
        logger.info('create an eth account')
        passwd = new_passwd()
        account = create_account(passwd)

    return account
