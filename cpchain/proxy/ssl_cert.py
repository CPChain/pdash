import os
import logging

from cpchain import config
from cpchain.utils import join_with_rc, join_with_root

logger = logging.getLogger(__name__)

def get_ssl_cert():
    server_key = os.path.expanduser(
        join_with_rc(config.proxy.server_key))
    server_crt = os.path.expanduser(
        join_with_rc(config.proxy.server_crt))

    if not os.path.isfile(server_key):
        logger.info("SSL key/cert file not found, "
                    + "run local self-test by default")
        server_key_sample = 'cpchain/assets/proxy/key/server.key'
        server_crt_sample = 'cpchain/assets/proxy/key/server.crt'
        server_key = join_with_root(server_key_sample)
        server_crt = join_with_root(server_crt_sample)

    return server_key, server_crt
