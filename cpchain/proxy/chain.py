import logging

from cpchain import chain, config
from cpchain.proxy.account import get_proxy_id

logger = logging.getLogger(__name__)

_proxy_agent = None

def get_proxy_agent():
    global _proxy_agent # pylint: disable=global-statement

    if not _proxy_agent:
        w3 = chain.utils.default_w3
        bin_path = chain.utils.join_with_root(config.chain.contract_bin_path)
        contract_name = config.chain.contract_name

        _proxy_agent = chain.agents.ProxyAgent(
            w3,
            bin_path,
            contract_name,
            account=get_proxy_id())

    return _proxy_agent

def order_is_ready_on_chain(order_id):
    try:
        e = get_proxy_agent().check_order_is_ready(order_id)
    except:
        logger.exception("failed to query order %d on chain" % order_id)
        return False

    return e

def claim_data_fetched_to_chain(order_id):
    try:
        get_proxy_agent().claim_fetched(order_id)
        record = get_proxy_agent().query_order(order_id)
    except:
        logger.exception("failed to claim fetched order %d to chain" % order_id)
        return False

    if record[10] == 2:
        return True

    return False

def claim_data_delivered_to_chain(order_id, signature=None):

    signature = signature or b'dummy'
    try:
        get_proxy_agent().claim_delivered(order_id, signature)
        record = get_proxy_agent().query_order(order_id)
    except:
        logger.exception("failed to claim delivered order %d to chain" % order_id)
        return False

    if record[10] == 3:
        return True

    return False
