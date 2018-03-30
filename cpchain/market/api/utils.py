import hashlib


def md5(source):
    digest = hashlib.md5()
    digest.update(source)
    return digest.hexdigest()
