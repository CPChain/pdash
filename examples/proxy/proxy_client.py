import sys

from twisted.python import log
from twisted.internet import defer

from cpchain.utils import reactor

from cpchain.account import Accounts
from cpchain.crypto import ECCipher
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
listcp
from cpchain.proxy.client import pick_proxy, get_proxy_addr, concat_url, ProxyClient, download_file

log.startLogging(sys.stdout)

order_id = 1
order_type = 'stream'

accounts = Accounts()
buyer_account = accounts[0]
seller_account = accounts[1]

buyer_private_key = buyer_account.private_key  #object type
buyer_public_key = ECCipher.serialize_public_key(
    buyer_account.public_key)    # string type
buyer_addr = ECCipher.get_address_from_public_key(
    buyer_account.public_key)  #string type

seller_private_key = seller_account.private_key
seller_public_key = ECCipher.serialize_public_key(
    seller_account.public_key)   #string type
seller_addr = ECCipher.get_address_from_public_key(
    seller_account.public_key)  #string type

@defer.inlineCallbacks
def seller_request():
    # seller_request
    message = Message()
    seller_data = message.seller_data
    message.type = Message.SELLER_DATA
    seller_data.order_id = order_id
    seller_data.order_type = order_type
    seller_data.seller_addr = seller_addr
    seller_data.buyer_addr = buyer_addr
    seller_data.market_hash = 'MARKET_HASH'
    seller_data.AES_key = b'AES_key'

    # storage = seller_data.storage

    # # ipfs storage
    # storage.type = 'ipfs'

    # import importlib
    # storage_plugin = "cpchain.storage-plugin."
    # module = importlib.import_module(storage_plugin + storage.type)
    # s = module.Storage()
    # param = s.user_input_param()
    # storage.file_uri = s.upload_file('/bin/bash', param)

    # # S3 storage
    # storage.type = 's3'

    # import importlib
    # storage_plugin = "cpchain.storage-plugin."
    # module = importlib.import_module(storage_plugin + storage.type)
    # s = module.Storage()
    # param = s.user_input_param()
    # storage.file_uri  = s.upload_file('/bin/bash', param)

    sign_message = SignMessage()
    sign_message.public_key = seller_public_key
    sign_message.data = message.SerializeToString()
    sign_message.signature = ECCipher.create_signature(
        seller_private_key,
        sign_message.data
        )

    proxy_id = yield pick_proxy()
    proxy_addr = yield get_proxy_addr(proxy_id)

    if proxy_addr:
        proxy_client = ProxyClient(proxy_addr)
        proxy_reply = yield proxy_client.run(sign_message)
        proxy_client.stop()

        if not proxy_reply.error:
            print('AES_Key: %s' % proxy_reply.AES_key)
            ip = proxy_addr[0]
            urls = concat_url(ip, proxy_reply)
            print(urls)
        else:
            print(proxy_reply.error)

    buyer_request()

@defer.inlineCallbacks
def buyer_request():
    message = Message()
    buyer_data = message.buyer_data
    message.type = Message.BUYER_DATA
    buyer_data.order_id = order_id
    buyer_data.order_type = order_type
    buyer_data.seller_addr = seller_addr
    buyer_data.buyer_addr = buyer_addr
    buyer_data.market_hash = 'MARKET_HASH'

    sign_message = SignMessage()
    sign_message.public_key = buyer_public_key
    sign_message.data = message.SerializeToString()
    sign_message.signature = ECCipher.create_signature(
        buyer_private_key,
        sign_message.data
        )

    proxy_id = yield pick_proxy()
    proxy_addr = yield get_proxy_addr(proxy_id)

    if proxy_addr:
        proxy_client = ProxyClient(proxy_addr)
        proxy_reply = yield proxy_client.run(sign_message)
        proxy_client.stop()

        if not proxy_reply.error:
            print('AES_Key: %s' % proxy_reply.AES_key)
            ip = proxy_addr[0]
            urls = concat_url(ip, proxy_reply)
            print(urls)
            if order_type == 'file':
                yield download_file(urls[0])
        else:
            print(proxy_reply.error)

seller_request()

try:
    reactor.run()
except KeyboardInterrupt:
    pass
finally:
    pass
