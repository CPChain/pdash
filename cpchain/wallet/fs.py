import tempfile
import os
import logging
import importlib
import hashlib
import json
from cpchain.wallet.db import get_session, FileInfo, create_engine, sessionmaker, BuyerFileInfo, CollectInfo, FileInfoVersion
from cpchain.crypto import AESCipher, RSACipher
from cpchain.utils import join_with_rc
from cpchain import config

logger = logging.getLogger(__name__)


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

def get_file_by_market_hash(market_hash):
    return get_session().query(FileInfo).filter(FileInfo.market_hash == market_hash)


def get_file_id_new(file_id):
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
    session = get_session()
    session.add(new_file_info)
    session.commit()


def update_file_info_version(public_key):
    try:
        session = get_session()
        public_key_list = []
        for key in session.query(FileInfoVersion).all():
            public_key_list.append(key.public_key)
        if public_key not in public_key_list:
            new_user_version = FileInfoVersion(version=1, public_key=public_key)
            add_file(new_user_version)
        else:
            cur_version = session.query(FileInfoVersion).filter(FileInfoVersion.public_key == public_key)
            session.query(FileInfoVersion).filter(FileInfoVersion.public_key == public_key). \
                update({FileInfoVersion.version: cur_version+1}, synchronize_session=False)
            session.commit()
    except:
        logger.exception("update_file_info_version error")


def publish_file_update(market_hash, selected_id):
    try:
        session = get_session()
        session.query(FileInfo).filter(FileInfo.id == selected_id). \
            update({FileInfo.market_hash: market_hash, FileInfo.is_published: True}, synchronize_session=False)
        session.commit()
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

def upload_file(file_path, storage_type, dest, data_name=None):
    # fixed previous bugs of temporary file being deleted after function return
    tmp = tempfile.NamedTemporaryFile(delete=True)
    encrypted_path = tmp.name
    this_key = encrypt_file(file_path, encrypted_path)
    storage_module = importlib.import_module(
        "cpchain.storage-plugin." + storage_type
    )
    storage = storage_module.Storage()
    file_uri = yield storage.upload_data(encrypted_path, dest)  # d_upload file_uri: string save directly
    file_name = list(os.path.split(file_path))[-1]
    file_size = os.path.getsize(file_path)
    logger.debug('start to write data into database')
    if data_name:
        file_name = data_name
    file_md5 = hashlib.md5(open(encrypted_path, "rb").read()).hexdigest()
    hashcode = json.loads(file_uri)
    hashcode['file_hash'] = file_md5
    new_file_info = FileInfo(hashcode=json.dumps(hashcode), name=file_name, path=file_path, size=file_size,
                             remote_type=str(storage_type), remote_uri=str(file_uri),
                             is_published=False, aes_key=this_key)
    add_file(new_file_info)
    logger.debug('file id: %s', new_file_info.id)
    tmp.close()
    file_id = new_file_info.id
    return file_id

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
    logger.debug("Collect record (id = %s) has been deleted !", file_id)


def buyer_file_update(file_title):
    try:
        session = get_session()
        session.query(BuyerFileInfo).filter(BuyerFileInfo.file_title == file_title). \
            update({BuyerFileInfo.is_downloaded: True}, synchronize_session=False)
        session.commit()
    except:
        logger.exception("error publish_file_update")
