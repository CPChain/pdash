import sys, os
import ipfsapi

from cpchain import config, root_dir

class IPFS(object):
    def __init__(self):
        self.client = None

    def connect(self, host=config.storage.ipfs.addr,
                port=config.storage.ipfs.port):

        try:
            self.client = ipfsapi.connect(host, port)
        except:
            sys.stderr.write(sys.exc_info())
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
            sys.stderr.write(sys.exc_info())
            return False
        else:
            return True

    def add_file(self, file_path):
        if not self.client:
            sys.stderr.write("invalid ipfs client")
            return

        if os.path.isdir(file_path):
            try:
                file_nodes = self.client.add(file_path, recursive=True)
            except:
                errorno = sys.exc_info()
                sys.stderr.write(errorno)
            else:
                return file_nodes[-1]['Hash']
        elif os.path.isfile(file_path):
            try:
                file_node = self.client.add(file_path)
            except:
                errorno = sys.exc_info()
                sys.stderr.write(errorno)
            else:
                return file_node['Hash']
        else:
            sys.stderr.write('invalid file path')


    def get_file(self, file_hash,
                file_dir=os.path.join(root_dir,
                config.proxy.server_root)):
        if not self.file_in_ipfs(file_hash):
            return False

        if os.path.isdir(file_dir):
            cwd = os.getcwd()
            os.chdir(file_dir)
            try:
                self.client.get(file_hash)
            except:
                errorno = sys.exc_info()
                sys.stderr.write(errorno)
                os.chdir(cwd)
                return False
            else:
                os.chdir(cwd)
                return True

        else:
            sys.stderr.write('invalid file directory')

        return False

