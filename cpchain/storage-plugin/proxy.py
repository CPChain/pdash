import treq
from zope.interface import implementer

from twisted.web.iweb import IPolicyForHTTPS

from twisted.internet import defer, ssl

from cpchain.proxy.client import pick_proxy, get_proxy
# from cpchain.proxy.client import upload_file
# from cpchain.proxy.client import download_file

@implementer(IPolicyForHTTPS)
class NoVerifySSLContextFactory(object):
    """Context that doesn't verify SSL connections"""
    def creatorForNetloc(self, hostname, port): # pylint: disable=unused-argument
        return ssl.CertificateOptions(verify=False)

def no_verify_agent(**kwargs):
    reactor = treq.api.default_reactor(kwargs.get('reactor'))
    pool = treq.api.default_pool(
        reactor,
        kwargs.get('pool'),
        kwargs.get('persistent'))

    no_verify_agent.agent = treq.api.Agent(
        reactor,
        contextFactory=NoVerifySSLContextFactory(),
        pool=pool
    )
    return no_verify_agent.agent

class Storage:
    @defer.inlineCallbacks
    def user_input_param(self):
        proxy_id = yield pick_proxy()
        return {
            'proxy_id': proxy_id
            }

    @defer.inlineCallbacks
    def upload_file(self, src, dst):
        proxy_id = dst['proxy_id']

        proxy_addr = yield get_proxy(proxy_id)

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
    def download_file(self, src, dst):

        f = open(dst, 'wb')
        resp = yield treq.get(src, agent=no_verify_agent())
        yield treq.collect(resp, f.write)
        f.close()
