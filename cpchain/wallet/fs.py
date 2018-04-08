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


def delete_file(file_name):
    session.query(FileInfo).filter(FileInfo.name == file_name).\
        delete(synchronize_session=False)
    session.commit()


def encrypt_file(key, file_in_path, file_out_path):
    encrypter = AESCipher(key=key)
    encrypter.encrypt(file_in_path, file_out_path)


def decrypt_file(key, file_in_path, file_out_path):
    decrypter = AESCipher(key=key)
    decrypter.decrypt(file_in_path, file_out_path)


def upload_file_ipfs(file_path):
    storage = IPFSStorage()
    storage.upload_file(file_path)


def download_file_ipfs(fhash, file_path):
    storage = IPFSStorage()
    return storage.download_file(fhash=fhash, fpath=file_path)


