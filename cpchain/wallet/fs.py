import tempfile

from cpchain.wallet.db import session, FileInfo, osp, create_engine, sessionmaker
from cpchain.crypto import AESCipher
from cpchain.proxy.ipfs import *


def get_file_list():
    """This returns a list of files.
    """
    return session.query(FileInfo).all()


# Return the file names in a tuple
def get_file_names():
    return list(zip(*session.query(FileInfo.name).all()))[0]


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
        ipfs_client = IPFS()
        ipfs_client.connect()
        file_hash = ipfs_client.add_file(encrypted_path)
    file_name = list(os.path.split(file_path))[-1]
    file_size = os.path.getsize(file_path)
    new_file_info = FileInfo(hashcode=str(file_hash), name=file_name, path=file_path, size=file_size,
                             remote_type="ipfs", remote_uri="/ipfs/" + file_name, is_published=False, aes_key=this_key)
    add_file(new_file_info)
    return file_hash


def download_file_ipfs(fhash, file_path):
    ipfs_client = IPFS()
    ipfs_client.connect()
    if ipfs_client.file_in_ipfs(fhash):
        return ipfs_client.get_file(fhash, file_path)
    else:
        return False


