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
            account = Account(key_path=key_path, key_passphrase=key_passphrase)
            self.append(account)

        if len(self):
            self.default_account = self[0]

    def set_default_account(self, idx):
        assert idx < len(self)
        self.default_account = self[idx]


class Account:
    def __init__(self, key_path=None, key_passphrase=None, private_key=None):

        if key_passphrase:
            self.key_passphrase = key_passphrase

        if private_key:
            self.private_key = crypto.ECCipher.create_private_key(private_key)
            self.public_key = crypto.ECCipher.create_public_key_from_private_key(self.private_key)

        elif key_path:
            if not key_passphrase:
                key_passphrase = input("Input Key Passphrase: ")
                self.key_passphrase = key_passphrase
            self.key_path = key_path
            self.private_key, self.public_key = crypto.ECCipher.load_key_pair(key_path, key_passphrase)


def unlock_account(account):
    addr = crypto.ECCipher.get_address_from_public_key(account.public_key)
    web3.personal.unlockAccount(web3.toChecksumAddress(addr), account.key_passphrase)

def lock_account(account):
    addr = crypto.ECCipher.get_address_from_public_key(account.public_key)
    web3.personal.lockAccount(web3.toChecksumAddress(addr))

def create_account(passwd, filepath=_keystore_dir, name=None):

    acct = web3.eth.account.create()

    try:
        web3.personal.importRawKey(acct.privateKey, passwd)
    except:
        logger.info("account already in node's keychain")

    if not name:
        name = "UTC--%s--%s" % (datetime.utcnow().isoformat(), acct.address[2:].lower())

    # follow eth keystore naming rule
    # go-ethereum/accounts/keystore/key.go:208
    # // keyFileName implements the naming convention for keyfiles:
    # // UTC--<created_at UTC ISO8601>-<address hex>
    # func keyFileName(keyAddr common.Address) string {
    #     ts := time.Now().UTC()
    #     return fmt.Sprintf("UTC--%s--%s", toISO8601(ts), hex.EncodeToString(keyAddr[:]))
    # }

    key_file = osp.join(
        filepath,
        name
    )
    encrypted_key = web3.eth.account.encrypt(acct.privateKey, passwd)

    with open(key_file, 'w') as f:
        f.write(json.dumps(encrypted_key))

    account = Account(key_passphrase=passwd, private_key=acct.privateKey)
    account.key_path = key_file
    return account


def import_account(key_file, passwd):

    with open(key_file) as f:
        encrypted_key = json.load(f)

    private_key = web3.eth.account.decrypt(encrypted_key, passwd)
    acct = web3.eth.account.privateKeyToAccount(private_key)

    try:
        web3.personal.importRawKey(acct.privateKey, passwd)
    except:
        logger.info("account already in node's keychain")

    account = Account(key_passphrase=passwd, private_key=acct.privateKey)
    account.key_path = key_file
    return account

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

def get_balance(account):
    if not web3:
        return 0
    return web3.eth.getBalance(account)

def send_tranaction(from_account, to_account, value):
    transaction = {
        'from': from_account,
        'to': to_account,
        'value': value
    }

    # TODO: should change to web3.personal.sendTransaction(transaction, passphrase) in future.
    web3.eth.sendTransaction(transaction)

def scan_transaction(start_block_id=None, end_block_id=None):
    # scan all blocks by default
    start_block_id = start_block_id or 0
    end_block_id = end_block_id or web3.eth.blockNumber

    for block_id in range(start_block_id, end_block_id + 1):
        timestamp = web3.eth.getBlock(block_id).timestamp
        timestamp = datetime.fromtimestamp(timestamp).isoformat()
        transaction_cnt = web3.eth.getBlockTransactionCount(block_id)
        if transaction_cnt == 0:
            yield block_id
        for transaction_id in range(0, transaction_cnt):
            transaction = web3.eth.getTransactionByBlock(block_id, transaction_id)
            txhash = transaction.hash.hex()
            to_account = transaction.to
            # can't use transaction.from, for from is a reserverd keyword in python
            from_account = transaction['from']
            value = transaction.value
            txfee = transaction.gas / transaction.gasPrice
            # follow ethersacn.io output format
            yield {
                    'txhash': txhash,
                    'block': block_id,
                    'date': timestamp,
                    'from': from_account,
                    'to': to_account,
                    'value': value,
                    'txfee': txfee
                }

def to_ether(value):
    return web3.fromWei(value, 'ether')

