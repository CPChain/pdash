import os
import glob
import json
from datetime import datetime

from cpchain.chain.utils import default_w3 as w3
from eth_account.messages import defunct_hash_message

def new_account():
    '''[summary]

    Returns:
        [type]: [description]
    '''

    return w3.eth.account.create()

def export_account(account, keystore_dir, passphrase):

    file_name = "UTC--%s--%s" % (datetime.utcnow().isoformat(), account.address[2:].lower())

    keystore = os.path.join(keystore_dir, file_name)

    encrypted_key = w3.eth.account.encrypt(account.privateKey, passphrase)

    with open(keystore, 'w') as f:
        f.write(json.dumps(encrypted_key))

def import_account(keystore, passphrase):
    with open(keystore) as f:
        encrypted_key = json.load(f)

    private_key = w3.eth.account.decrypt(encrypted_key, passphrase)
    account = w3.eth.account.privateKeyToAccount(private_key)

    return account

def get_keystore_list(keystore_dir):
    ptn = os.path.join(keystore_dir, 'UTC-*')
    return glob.glob(ptn)

def send_raw_transaction(account, to, value, gas=100000, gasPrice=10000000000):
    transaction = {
            'to': to,
            'value': value,
            'gas': gas,
            'gasPrice': gasPrice,
            'nonce': w3.eth.getTransactionCount(account.address)
    }

    signed = w3.eth.account.signTransaction(transaction, account.privateKey)

    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)

    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash.hex())
    if tx_receipt.status == 0:
        return False
    else:
        return True

def create_signature(account, primitive=None, hexstr=None, text=None):
    '''Sign a Message using accout private key

    Args:
        account ([type]): ETH account
        primitive ([bytes or int]): the binary message to be signed
        hexstr ([hexstr]): the message encoded as hex
        text ([text]): the message as a series of unicode characters (a normal Py3 str)

    Returns:
        [hexstr]: signature
    '''
    msg_hash = defunct_hash_message(primitive, hexstr, text)
    signed_msg = w3.eth.account.signHash(msg_hash, private_key=account.privateKey)

    return w3.toHex(signed_msg.signature)

def verify_sign(address, signature, primitive=None, hexstr=None, text=None):

    msg_hash = defunct_hash_message(primitive, hexstr, text)
    signature = w3.toBytes(hexstr=signature)
    return address == w3.eth.account.recoverHash(msg_hash, signature=signature)
