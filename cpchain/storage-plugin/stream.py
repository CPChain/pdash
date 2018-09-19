import json

import subprocess

from uuid import uuid1 as uuid

from twisted.internet import defer

from cpchain.proxy.client import pick_proxy, get_proxy
from cpchain.utils import join_with_root


class Storage:
    data_type = 'stream'

    @defer.inlineCallbacks
    def user_input_param(self):
        proxy_id = yield pick_proxy()
        return {
            'proxy_id': proxy_id
            }

    @defer.inlineCallbacks
    def upload_data(self, src, dst):
        proxy_id = dst['proxy_id']

        proxy_addr = yield get_proxy(proxy_id)

        if proxy_addr:
            stream_id = str(uuid())

            # proxy addr format: (ip, ctrl_port, file_port, stream_ws_port, stream_restful_port)
            ws_url = 'ws://%s:%d/%s' % (str(proxy_addr[0]), int(proxy_addr[3]), stream_id)
            rest_url = 'http://%s:%d/%s' % (str(proxy_addr[0]), int(proxy_addr[4]), stream_id)

            return json.dumps(
                {
                    'ws_url': ws_url,
                    'restful_url': rest_url
                }
            )

    def download_data(self, src, dst):
        stream_channel = json.loads(src)
        ws_url = stream_channel['ws_url']
        dest_stream_id = dst

        cmd_path = join_with_root('cpchain/storage-plugin/bin/replicate-stream')
        args = ['nohup', cmd_path, ws_url, dest_stream_id]
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
