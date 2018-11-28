import os
import time
import glob
import json
from datetime import datetime

from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred
from twisted.internet.threads import deferToThread

from cpchain.utils import reactor, join_with_rc, config
from cpchain.chain.utils import default_w3 as w3

_passphrase = 'cpc'
_keystore_dir = join_with_rc(config.account.keystore_dir)
os.makedirs(_keystore_dir, exist_ok=True)

def create_eth_account():
    return w3.eth.account.create()

def backup_eth_account(eth_account, passphrase=_passphrase, keystore_dir=_keystore_dir):

    file_name = "UTC--%s--%s" % (datetime.utcnow().isoformat(), eth_account.address[2:].lower())

    keystore = os.path.join(keystore_dir, file_name)

    encrypted_key = w3.eth.account.encrypt(eth_account.privateKey, passphrase)

    with open(keystore, 'w') as f:
        f.write(json.dumps(encrypted_key))

def get_keystore_list(keystore_dir=_keystore_dir):
    ptn = os.path.join(keystore_dir, 'UTC-*')
    return glob.glob(ptn)

def load_eth_account(keystore, passphrase=_passphrase):
    with open(keystore) as f:
        encrypted_key = json.load(f)

    private_key = w3.eth.account.decrypt(encrypted_key, passphrase)
    eth_account = w3.eth.account.privateKeyToAccount(private_key)

    return eth_account

def load_eth_account_list(account_num):

    eth_account_list = []
    ds = []

    for keystore in get_keystore_list():
        d = deferToThread(load_eth_account, keystore)
        ds.append(d)
        # eth_account_list.append(load_eth_account(keystore))
        account_num -= 1
        if account_num == 0:
            break

    def handle_result(result):
        for (success, value) in result:
            if success:
                account = value
                print('Loading account success: ', account.address)
                eth_account_list.append(account)
            else:
                print('Loading account failure: ', value.getErrorMessage())

        return eth_account_list

    if ds:
        dl = DeferredList(ds, consumeErrors=True)
        dl.addCallback(handle_result)
    else:
        dl = Deferred()
        dl.callback([])

    return dl

def prepare_eth_account():
    ETH = 10**18

    eth_account = create_eth_account()
    transaction = {
        'from': w3.eth.coinbase,
        'to': eth_account.address,
        'value': 100000 * ETH
        }

    w3.personal.sendTransaction(transaction, _passphrase)

    # TODO: to be removed when PDASH swithing to eth.sendRawTransaction()
    w3.personal.importRawKey(eth_account.privateKey, _passphrase)

    backup_eth_account(eth_account)

    return eth_account

def prepare_eth_account_list(account_num):
    eth_account_list = []
    ds = []

    for i in range(0, account_num):
        d = deferToThread(prepare_eth_account)
        ds.append(d)
        account_num -= 1
        if account_num == 0:
            break

    def handle_result(result):
        for (success, value) in result:
            if success:
                account = value
                print('Creating account success: ', account.address)
                eth_account_list.append(account)
            else:
                print('Creating account failure: ', value.getErrorMessage())

        return eth_account_list

    if ds:
        dl = DeferredList(ds, consumeErrors=True)
        dl.addCallback(handle_result)

    return dl


@inlineCallbacks
def create_test_accounts(account_num, passphrase=_passphrase):
    eth_account_list = yield load_eth_account_list(account_num)

    if len(eth_account_list) < account_num:
        missing_num = account_num - len(eth_account_list)
        missing_account_list = yield prepare_eth_account_list(missing_num)
        eth_account_list += missing_account_list

    print('eth accout list for testing is ready.')

    return eth_account_list

@inlineCallbacks
def main():
    eth_account_list = yield create_test_accounts(100)
    for account in eth_account_list:
        print(account.address)


if __name__ == '__main__':

    main()

    reactor.run()
