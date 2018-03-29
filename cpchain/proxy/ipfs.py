import sys, os
import ipfsapi

from cpchain import config

def ipfs_connect(host, port):
    host = host or config.storage.ipfs.addr
    port = port or config.storage.ipfs.port

    try:
        client = ipfsapi.connect(host, port)

    except:
           errorno = sys.exc_info()
           sys.stderr.write(errorno)
    else:
        return client

def ipfs_add_files(client, file_path):
    if not client:
        sys.stderr.write("invalid ipfs client")
        return

    if os.path.isdir(file_path):
        try:
            files = client.add(file_path, recursive=True)
        except:
            errorno = sys.exc_info()
            sys.stderr.write(errorno)
        else:
            return files
    elif os.path.isfile(file_path):
        try:
            files = client.add(file_path, recursive=False)
        except:
            errorno = sys.exc_info()
            sys.stderr.write(errorno)
        else:
            return files
    else:
        sys.stderr.write('invalid file path')

def ipfs_ls_files(client, file_hash):
    if not client:
        sys.stderr.write("invalid ipfs client")
        return

    try:
        file_objects = client.ls(file_hash)
    except:
        errorno = sys.exc_info()
        sys.stderr.write(errorno)
    else:
        return file_objects

def ipfs_cat_files(client, file_hash):
    if not client:
        sys.stderr.write("invalid ipfs client")
        return

    try:
        file_contents = client.cat(file_hash)
    except:
        errorno = sys.exc_info()
        sys.stderr.write(errorno)
    else:
        return file_contents

def ipfs_get_files_hash(files):
    if type(files) == list:
        files_hash = []
        for f in files:
            if 'Hash' in f:
                files_hash.append(f['Hash'])
        return files_hash
    elif type(files) == dict:
        if 'Hash' in files:
            return files['Hash']
    else:
        sys.stderr.write('invalid files parameter')

def ipfs_get_files(client, file_hash, file_dir):
    if not client:
        sys.stderr.write("invalid ipfs client")
        return

    if os.path.isdir(file_dir):
        cwd = os.getcwd()
        os.chdir(file_dir)
        try:
            client.get(file_hash)
        except:
            errorno = sys.exc_info()
            sys.stderr.write(errorno)

        os.chdir(cwd)

    else:
        sys.stderr.write('invalid file directory')

def is_file_in_ipfs(host, port, file_hash):
    host = host or config.storage.ipfs.addr
    port = port or config.storage.ipfs.port

    if not host or not port:
        sys.stderr.write('invalid ipfs gateway')
        return

    client = ipfs_connect(host, port)
    if client:
        file_object = ipfs_ls_files(client, file_hash)
        if file_object:
            return True

    return False

def read_ipfs_files(host, port, file_hash):
    host = host or config.storage.ipfs.addr
    port = port or config.storage.ipfs.port

    if not host or not port:
        sys.stderr.write('invalid ipfs gateway')
        return

    client = ipfs_connect(host, port)
    if client:
        file_content = ipfs_cat_files(client, file_hash)
        if file_content:
            return file_content
