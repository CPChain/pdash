import tempfile
import os
import logging

from cpchain.wallet.db import get_session, FileInfo, osp, create_engine, sessionmaker, BuyerFileInfo, CollectInfo, FileInfoVersion
from cpchain.crypto import AESCipher, RSACipher
from cpchain.utils import Encoder, join_with_rc
from cpchain.storage import IPFSStorage
from cpchain.storage import S3Storage
from cpchain import root_dir, config

logger = logging.getLogger(__name__)  # pylint: disable=locally-disabled, invalid-name


def get_file_list():
    """This returns a list of files.
    """
    dbpath = join_with_rc(config.wallet.dbpath)
    engine = create_engine('sqlite:///{dbpath}'.format(dbpath=dbpath), echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session.query(FileInfo).all()


def get_file_by_id(file_id):
    return get_session().query(FileInfo).filter(FileInfo.id == file_id).all()[0]


def get_file_by_hash(file_hash):
    return get_session().query(FileInfo).filter(FileInfo.hashcode == file_hash)

def get_file_id_new(file_id):
    dbpath = join_with_rc(config.wallet.dbpath)
    engine = create_engine('sqlite:///{dbpath}'.format(dbpath=dbpath), echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return get_session().query(FileInfo).filter(FileInfo.id == file_id).all()[0]

def get_buyer_file_list():
    return get_session().query(BuyerFileInfo).all()


# Return the file names in a tuple
def get_file_names():
    return list(zip(*get_session().query(FileInfo.name).all()))[0]


# Return the file names in a tuple
def get_buyer_file_names():
    return list(zip(*get_session().query(BuyerFileInfo.name).all()))[0]


def add_file(new_file_info):
    # dbpath = join_with_rc(config.wallet.dbpath)
    # engine = create_engine('sqlite:///{dbpath}'.format(dbpath=dbpath), echo=True)
    session = get_session()
    session.add(new_file_info)
    session.commit()


def update_file_info_version(public_key):
    # dbpath = join_with_rc(config.wallet.dbpath)
    # engine = create_engine('sqlite:///{dbpath}'.format(dbpath=dbpath), echo=True)
    # Session = sessionmaker(bind=engine)
    # session = Session()
    try:
        session = get_session()
        public_key_list = []
        for key in session.query(FileInfoVersion).all():
            public_key_list.append(key.public_key)
        if public_key not in public_key_list:
            new_user_version = FileInfoVersion(version=1, public_key=public_key)
            add_file(new_user_version)
        else:
            cur_version = session.query(FileInfoVersion).filter(FileInfoVersion.public_key==public_key)
            session.query(FileInfoVersion).filter(FileInfoVersion.public_key==public_key). \
                update({FileInfoVersion.version: cur_version+1}, synchronize_session=False)
            session.commit()
    except:
        logger.exception("update_file_info_version error")


def publish_file_update(market_hash, selected_id):
    try:
        logger.debug("333333333333333333333333xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        # dbpath = join_with_rc(config.wallet.dbpath)
        # engine = create_engine('sqlite:///{dbpath}'.format(dbpath=dbpath), echo=True)
        session = get_session()
        session.query(FileInfo).filter(FileInfo.id == selected_id). \
            update({FileInfo.market_hash: market_hash, FileInfo.is_published: True}, synchronize_session=False)
        session.commit()
        logger.debug("444444xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    except:
        logger.exception("error publish_file_update")

def delete_file(file_name):
    session = get_session()
    session.query(FileInfo).filter(FileInfo.name == file_name).\
        delete(synchronize_session=False)
    session.commit()

def delete_file_by_id(file_id):
    session = get_session()
    session.query(FileInfo).filter(FileInfo.id == file_id). \
        delete(synchronize_session=False)
    session.commit()

def delete_file_by_msh(market_hash):
    session = get_session()
    session.query(FileInfo).filter(FileInfo.market_hash == market_hash). \
        delete(synchronize_session=False)
    session.commit()


def delete_buyer_file(file_name):
    session = get_session()
    session.query(BuyerFileInfo).filter(BuyerFileInfo.file_title == file_name). \
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
    session = get_session()
    aes_key = session.query(FileInfo.aes_key).filter(FileInfo.path == file_in_path).first()[0]
    decrypter = AESCipher(aes_key)
    decrypter.decrypt(file_in_path, file_out_path)


def upload_file_ipfs(file_path):
    with tempfile.TemporaryDirectory() as tmpdirname:
        encrypted_path = os.path.join(tmpdirname, 'encrypted.txt')
        logger.debug("start to encrypt")
        this_key = encrypt_file(file_path, encrypted_path)
        logger.debug("encrypt completed")
        ipfs_client = IPFSStorage()
        ipfs_client.connect()
        file_hash = ipfs_client.upload_file(encrypted_path)
    file_name = list(os.path.split(file_path))[-1]
    file_size = os.path.getsize(file_path)
    logger.debug('start to write data into database')
    new_file_info = FileInfo(hashcode=str(file_hash), name=file_name, path=file_path, size=file_size,
                             remote_type="ipfs", remote_uri="/ipfs/" + file_hash,
                             is_published=False, aes_key=this_key)
    add_file(new_file_info)
    logger.debug('file id: %s', new_file_info.id)
    file_id = new_file_info.id
    return file_id


def upload_file_s3(file_path):
    with tempfile.TemporaryDirectory() as tmpdirname:
        encrypted_path = os.path.join(tmpdirname, 'encrypted.txt')
        logger.debug("start to encrypt")
        this_key = encrypt_file(file_path, encrypted_path)
        logger.debug("encrypt completed")
        file_name = list(os.path.split(file_path))[-1]
        s3_client = S3Storage()
        try:
            s3_client.upload_file(encrypted_path, file_name, "cpchain-bucket")
        except Exception:
            logger.exception("verify signature error")
        else:
            pass

    file_name = list(os.path.split(file_path))[-1]
    file_size = os.path.getsize(file_path)
    logger.debug('start to write data into database')
    new_file_info = FileInfo(hashcode=str("s3_hash"), name=file_name, path=file_path, size=file_size,
                             remote_type="s3", remote_uri=file_name, is_published=False, aes_key=this_key)
    add_file(new_file_info)
    logger.debug('file id: %s', new_file_info.id)
    file_id = new_file_info.id
    return file_id


def download_file_ipfs(fhash, file_path):
    ipfs_client = IPFSStorage()
    ipfs_client.connect()
    if ipfs_client.file_in_ipfs(fhash):
        return ipfs_client.download_file(fhash, file_path)
    else:
        return False


# Decrypt aes key with rsa key then decrypt file with aes key.
def decrypt_file_aes(file_path, aes_key):
    decrypted_aes_key = RSACipher.decrypt(aes_key)
    print('In Decrypt file aes:' + str(len(decrypted_aes_key)))
    decrypter = AESCipher(decrypted_aes_key)
    decrypted_path = file_path + "_decrypted"
    decrypter.decrypt(file_path, decrypted_path)
    return decrypted_path

def add_record_collect(product_info):
    new_collect_info = CollectInfo(name=product_info['title'], price=product_info['price'], size=product_info['size'])
    add_file(new_collect_info)
    logger.debug("Adding new record to collectinfo successfully!")

def get_collect_list():
    """This returns a list of files.
    """
    session = get_session()
    return session.query(CollectInfo).all()

def delete_collect_id(file_id):
    session = get_session()
    session.query(CollectInfo).filter(CollectInfo.id == file_id). \
        delete(synchronize_session=False)
    session.commit()
    logger.debug("Collect record (id = {}) has been deleted !".format(file_id))

def buyer_file_update(file_uuid):
    try:
        # dbpath = join_with_rc(config.wallet.dbpath)
        # engine = create_engine('sqlite:///{dbpath}'.format(dbpath=dbpath), echo=True)
        session = get_session()
        session.query(BuyerFileInfo).filter(BuyerFileInfo.file_uuid == file_uuid). \
            update({BuyerFileInfo.is_downloaded: True}, synchronize_session=False)
        session.commit()
    except:
        logger.exception("error publish_file_update")
#
# # TODO Integrate download later
# def get_file_from_proxy(order_id, seller_public_key):
#
#     with open(join_with_root(config.wallet.private_key_path), "rb") as key_file:
#         buyer_private_key = serialization.load_pem_private_key(
#             key_file.read(),
#             password=b"cpchainisawesome",
#             backend=default_backend()
#         )
#
#     # buyer_trans = ProxyTrans(default_web3, config.chain.core_contract)
#     # buyer_public_key = buyer_trans.query_order(order_id)[1]
#     buyer_public_key = buyer_private_key.public_key()
#     message = Message()
#     buyer_data = message.buyer_data
#     message.type = Message.BUYER_DATA
#     buyer_data.seller_addr = seller_public_key
#     buyer_data.buyer_addr = buyer_public_key
#     buyer_data.market_hash = b'MARKET_HASH0123012345678012345'
#
#     sign_message = SignMessage()
#     sign_message.public_key = buyer_public_key
#     sign_message.data = message.SerializeToString()
#     sign_message.signature = ECCipher.generate_signature(
#         buyer_private_key,
#         sign_message.data
#     )
#
#     start_client(sign_message)
#     message = Message()
#     message.ParseFromString(sign_message.data)
#
#     proxy_reply = message.proxy_reply
#     if proxy_reply.error:
#         print(proxy_reply.error)
#     else:
#         print('AES_key: %s' % proxy_reply.AES_key.decode())
#         print('file_uuid: %s' % proxy_reply.file_uuid)
#
#     download_file(proxy_reply.file_uuid)
#
#     file_dir = os.path.expanduser(config.wallet.download_dir)
#     file_path = os.path.join(file_dir, proxy_reply.file_uuid)
#
#     # TODO Update database here
#
#     decrypted_aes_key = buyer_private_key.decrypt(proxy_reply.AES_key, padding.OAEP(
#         mgf=padding.MGF1(algorithm=hashes.SHA256()),
#         algorithm=hashes.SHA256(),
#         label=None)
#     )
#     decrypter = AESCipher(decrypted_aes_key)
#     decrypter.decrypt(file_dir, file_path + "decrypted")
#     return True
