import treq

from twisted.internet import defer

from cpchain.proxy.client import pick_proxy, get_proxy
from cpchain.proxy.ssl_cert import no_verify_agent

class Storage:
    data_type = 'file'

    @defer.inlineCallbacks
    def user_input_param(self, port=None):
        proxy_id = yield pick_proxy(port)
        return {
            'proxy_id': proxy_id
            }

    @defer.inlineCallbacks
    def upload_data(self, src, dst, port=None):
        proxy_id = dst['proxy_id']

        proxy_addr = yield get_proxy(proxy_id, port)

        if proxy_addr:
            # proxy addr format: (ip, ctrl_port, file_port, stream_ws_port, stream_restful_port)
            url = 'https://%s:%d' % (str(proxy_addr[0]), int(proxy_addr[2]))

            data = open(src, 'rb')
            resp = yield treq.post(url, agent=no_verify_agent(), data=data, stream=True)
            if resp:
                file_path = yield treq.text_content(resp)
                file_url = '%s/%s' % (url, file_path)

                return file_url

    @defer.inlineCallbacks
    def download_data(self, src, dst):

        f = open(dst, 'wb')
        resp = yield treq.get(src, agent=no_verify_agent())
        yield treq.collect(resp, f.write)
        f.close()
