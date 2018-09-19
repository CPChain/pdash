import os
import logging
import treq

from zope.interface import implementer
from twisted.web.iweb import IPolicyForHTTPS
from twisted.internet import ssl

from cpchain import config
from cpchain.utils import join_with_rc, join_with_root

logger = logging.getLogger(__name__)

def get_ssl_cert():
    server_key = join_with_rc(config.proxy.server_key)
    server_crt = join_with_rc(config.proxy.server_crt)

    if not os.path.isfile(server_key):
        logger.info("SSL key/cert file not found, "
                    + "run local self-test by default")
        server_key_sample = 'cpchain/assets/proxy/key/server.key'
        server_crt_sample = 'cpchain/assets/proxy/key/server.crt'
        server_key = join_with_root(server_key_sample)
        server_crt = join_with_root(server_crt_sample)

    return server_key, server_crt

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
