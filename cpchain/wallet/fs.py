from cpchain.wallet.db import session, FileInfo
from cpchain.crypto import AESCipher
from cpchain.storage import IPFSStorage, S3Storage


def get_file_list():
    """This returns a list of files.
    """
    return session.query(FileInfo.name).all()


def add_file(new_file):
    session.add(new_file)
    session.commit()
    return


def delete_file(file_name):
    session.query(FileInfo).filter(FileInfo.name == file_name).\
        delete(synchronize_session=False)
    session.commit()
    return


def encrypt_file(key, file_in_path, file_out_path):
    encrypter = AESCipher(key=key)
    encrypter.encrypt(file_in_path, file_out_path)
    return


def decrypt_file(key, file_in_path, file_out_path):
    decrypter = AESCipher(key=key)
    decrypter.decrypt(file_in_path, file_out_path)
    return


def upload_file(file_path, storage_type="IPFS"):
    if storage_type == "IPFS":
        storage = IPFSStorage()
    else:
        storage = S3Storage()
    storage.upload_file(file_path)
    return


def download_file(fhash, file_path, storage_type="IPFS"):
    if storage_type == "IPFS":
        storage = IPFSStorage()
    else:
        storage = S3Storage()
    storage.download_file(fhash=fhash, fpath=file_path)
    return

