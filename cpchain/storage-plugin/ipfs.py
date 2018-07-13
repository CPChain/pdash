import json
import os
import ipfsapi

class Storage:
    def user_input_param(self):
        # fixme: should get user input from UI

        param = {
            'host': '192.168.0.132',
            'port': 5001
        }

        return json.dumps(param)

    def upload_file(self, src, dst):
        dst = json.loads(dst)
        host = dst['host']
        port = dst['port']

        client = ipfsapi.connect(host, port)
        file_node = client.add(src)

        file_addr = {
            'host': host,
            'port': port,
            'file_hash': file_node['Hash']
        }

        return json.dumps(file_addr)

    def download_file(self, src, dst):
        src = json.loads(src)
        host = str(src['host'])
        port = int(src['port'])
        file_hash = str(src['file_hash'])

        client = ipfsapi.connect(host, port)
        client.get(file_hash)
        os.rename(file_hash, dst)
