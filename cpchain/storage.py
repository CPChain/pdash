import boto3
import ipfsapi

from cpchain import config

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
    def __init__(self, addr=None, port=None):
        addr = server or config.storage.ipfs.addr
        port = port or config.storage.ipfs.port
        # TODO make this non-blocking
        backend = ipfsapi.connect(addr, port)


    # cf. https://github.com/ipfs/py-ipfs-api
    def upload_file(self, fpath):
        return self.backend.add(fpath)
        

    def download_file(self, fhash, fpath):
        return self.backend.get(fhash, filepath=fpath)
