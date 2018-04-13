import tempfile, os

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.client import start_client, download_file
from cpchain.chain.trans import ProxyTrans
from cpchain.chain.utils import default_web3
from cpchain.wallet.db import session, FileInfo, osp, create_engine, sessionmaker, BuyerFileInfo
from cpchain.crypto import AESCipher, ECCipher
from cpchain.storage import IPFSStorage
from cpchain import root_dir, config
from cpchain.utils import join_with_root


def get_file_list():
    """This returns a list of files.
    """
    return session.query(FileInfo).all()


def get_buyer_file_list():
    return session.query(BuyerFileInfo).all()


# Return the file names in a tuple
def get_file_names():
    return list(zip(*session.query(FileInfo.name).all()))[0]


# Return the file names in a tuple
def get_buyer_file_names():
    return list(zip(*session.query(BuyerFileInfo.name).all()))[0]


def add_file(new_file_info):
    dbpath = osp.join(root_dir, config.wallet.dbpath)
    engine = create_engine('sqlite:///{dbpath}'.format(dbpath=dbpath), echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(new_file_info)
    session.commit()


def delete_file(file_name):
    session.query(FileInfo).filter(FileInfo.name == file_name).\
        delete(synchronize_session=False)
    session.commit()


def delete_buyer_file(file_name):
    session.query(FileInfo).filter(BuyerFileInfo.name == file_name). \
        delete(synchronize_session=False)
    session.commit()


# Generate a new key and encrypt the file with the key
def encrypt_file(file_in_path, file_out_path):
    new_key = AESCipher.generate_key()
    encrypter = AESCipher(new_key)
    encrypter.encrypt(file_in_path, file_out_path)
    return new_key


# Decrypt a file with key stored in database
def decrypt_file(file_in_path, file_out_path):
    aes_key = session.query(FileInfo.aes_key).filter(FileInfo.path == file_in_path).first()[0]
    decrypter = AESCipher(aes_key)
    decrypter.decrypt(file_in_path, file_out_path)


def upload_file_ipfs(file_path):
    with tempfile.TemporaryDirectory() as tmpdirname:
        encrypted_path = os.path.join(tmpdirname, 'encrypted.txt')
        this_key = encrypt_file(file_path, encrypted_path)
        ipfs_client = IPFSStorage()
        ipfs_client.connect()
        file_hash = ipfs_client.upload_file(encrypted_path)
    file_name = list(os.path.split(file_path))[-1]
    file_size = os.path.getsize(file_path)
    new_file_info = FileInfo(hashcode=str(file_hash), name=file_name, path=file_path, size=file_size,
                             remote_type="ipfs", remote_uri="/ipfs/" + file_name, is_published=False, aes_key=this_key)
    add_file(new_file_info)
    return file_hash


def download_file_ipfs(fhash, file_path):
    ipfs_client = IPFSStorage()
    ipfs_client.connect()
    if ipfs_client.file_in_ipfs(fhash):
        return ipfs_client.download_file(fhash, file_path)
    else:
        return False


def get_file_from_proxy(order_id, seller_public_key):

    with open(join_with_root(config.wallet.private_key_path), "rb") as key_file:
        buyer_private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    buyer_trans = ProxyTrans(default_web3, config.chain.core_contract)
    buyer_public_key = buyer_trans.query_order(order_id)[1]
    message = Message()
    buyer_data = message.buyer_data
    message.type = Message.BUYER_DATA
    buyer_data.seller_addr = seller_public_key
    buyer_data.buyer_addr = buyer_public_key
    buyer_data.market_hash = b'MARKET_HASH0123012345678012345'

    sign_message = SignMessage()
    sign_message.public_key = buyer_public_key
    sign_message.data = message.SerializeToString()
    sign_message.signature = ECCipher.generate_signature(
        buyer_private_key,
        sign_message.data
    )

    start_client(sign_message)
    message = Message()
    message.ParseFromString(sign_message.data)

    proxy_reply = message.proxy_reply
    if proxy_reply.error:
        print(proxy_reply.error)
    else:
        print('AES_key: %s' % proxy_reply.AES_key.decode())
        print('file_uuid: %s' % proxy_reply.file_uuid)

    download_file(proxy_reply.file_uuid)

    file_dir = os.path.expanduser(config.wallet.download_dir)
    file_path = os.path.join(file_dir, proxy_reply.file_uuid)

    # TODO Update database here

    with open(join_with_root(config.wallet.private_key_path), "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    decrypted_aes_key = private_key.decrypt(proxy_reply.AES_key, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None)
    )
    decrypter = AESCipher(decrypted_aes_key)
    decrypter.decrypt(file_dir, file_path + "decrypted")
    return True
