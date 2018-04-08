from cpchain.wallet.db import session, FileInfo
from cpchain.crypto import AESCipher
from cpchain.storage import IPFSStorage, S3Storage


def get_file_list():
    """This returns a list of files.
    """
    return session.query(FileInfo).all()


def get_file_names():
    return session.query(FileInfo.name).all()


def add_file(new_file_info):
    session.add(new_file_info)
    session.commit()


def delete_file(file_name):
    session.query(FileInfo).filter(FileInfo.name == file_name).\
        delete(synchronize_session=False)
    session.commit()


# Generate a new key and encrypt the file with the key
def encrypt_file(file_in_path, file_out_path):
    new_key = AESCipher.generate_key()
    encrypter = AESCipher(new_key)
    encrypter.encrypt(file_in_path, file_out_path)
    session.query(FileInfo).filter(FileInfo.path == file_in_path).\
        update({FileInfo.aes_key: new_key}, synchronize_session=False)
    session.commit()


# Decrypt a file with key stored in database
def decrypt_file(file_in_path, file_out_path):
    aes_key = str.encode(session.query(FileInfo.aes_key).
                         filter(FileInfo.path == file_in_path).first()[0])
    decrypter = AESCipher(aes_key)
    decrypter.decrypt(file_in_path, file_out_path)


def upload_file_ipfs(file_path):
    storage = IPFSStorage()
    storage.upload_file(file_path)


def download_file_ipfs(fhash, file_path):
    storage = IPFSStorage()
    return storage.download_file(fhash=fhash, fpath=file_path)


