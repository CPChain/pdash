import boto3
import ipfsapi

import sys, os
from cpchain import config, root_dir


class Storage:
    def __init__(self):
        pass

    def upload_file(self):
        raise NotImplementedError

    def download_file(self):
        raise NotImplementedError


class S3Storage(Storage):

    # cf. https://boto3.readthedocs.io/en/latest/guide/s3.html#using-the-transfer-manager
    class ProgressPercentage:

        def __init__(self, fpath, fsize=None):
            self.fpath = fpath

            import os
            self.fsize = fsize or os.path.getsize(fpath)

            self.bytes_seen_so_far = 0

            import threading
            self._lock = threading.Lock()

        def __call__(self, bytes_amount):
            with self._lock:
                self.bytes_seen_so_far += bytes_amount
                percentage = self.bytes_seen_so_far / self.fsize * 100


    def __init__(self, bucket=None, access_key_id=None, secret_access_key=None):
        super().__init__()
        # cf. https://joppot.info/2014/06/14/1621 for account creation.
        self.bucket = bucket or config.storage.s3.bucket

        access_key_id_ = access_key_id or config.storage.s3.access_key_id
        secret_access_key_ = secret_access_key or config.storage.s3.secret_access_key

        # cf. http://boto3.readthedocs.io/en/latest/guide/configuration.html
        self.s3 = boto3.client('s3',
                               aws_access_key_id=access_key_id_,
                               aws_secret_access_key=secret_access_key_)


    def upload_file(self, fpath, remote_fpath, bucket=None):
        self.s3.upload_file(fpath, bucket or self.bucket, remote_fpath, Callback=self.ProgressPercentage(fpath))


    def download_file(self, fpath, remote_fpath, fsize=None, bucket=None):
        if fsize:
            self.s3.download_file(bucket or self.bucket, remote_fpath, fpath, Callback=self.ProgressPercentage(fpath, fsize))
        else:
            self.s3.download_file(bucket or self.bucket, remote_fpath, fpath)


class IPFSStorage(Storage):
    def __init__(self):
        self.client = None

    def connect(self, host=None, port=None):
        host = host or config.storage.ipfs.addr
        port = port or config.storage.ipfs.port

        try:
            self.client = ipfsapi.connect(host, port)
        except:
            sys.stderr.write(str(sys.exc_info()))
            return False
        else:
            return True

    def file_in_ipfs(self, file_hash):
        if not self.client:
            sys.stderr.write("invalid ipfs client")
            return False

        try:
            self.client.ls(file_hash)
        except:
            sys.stderr.write(str(sys.exc_info()))
            return False
        else:
            return True

    def upload_file(self, file_path):
        if not self.client:
            sys.stderr.write("invalid ipfs client")
            return

        if os.path.isdir(file_path):
            try:
                file_nodes = self.client.add(file_path, recursive=True)
            except:
                sys.stderr.write(str(sys.exc_info()))
            else:
                return file_nodes[-1]['Hash']
        elif os.path.isfile(file_path):
            try:
                file_node = self.client.add(file_path)
            except:
                sys.stderr.write(str(sys.exc_info()))
            else:
                return file_node['Hash']
        else:
            sys.stderr.write('invalid file path')


    def download_file(self, file_hash, file_dir=None):
        if not self.file_in_ipfs(file_hash):
            return False

        file_dir = file_dir or os.getcwd()

        if os.path.isdir(file_dir):
            cwd = os.getcwd()
            os.chdir(file_dir)
            try:
                self.client.get(file_hash)
            except:
                sys.stderr.write(str(sys.exc_info()))
                os.chdir(cwd)
                return False
            else:
                os.chdir(cwd)
                return True

        else:
            sys.stderr.write('invalid file directory')

        return False
