import sys, os
import importlib

from twisted.python import log
from twisted.internet import defer

from cpchain.utils import reactor
from cpchain.utils import config, join_with_rc

from cpchain.account import Accounts
from cpchain.crypto import ECCipher
from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.client import pick_proxy, start_proxy_request, download_proxy_file

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

    storage = seller_data.storage

    #stream test
    storage.type = 'stream'

    storage_plugin = "cpchain.storage-plugin."
    module = importlib.import_module(storage_plugin + storage.type)
    s = module.Storage()
    param = yield s.user_input_param()
    param['proxy_id'] = param['proxy_id'][0] # should be selected by UI from proxy list
    storage.path = yield s.upload_data(None, param)

    # proxy storage
    # storage.type = 'proxy'

    # storage_plugin = "cpchain.storage_plugin."
    # module = importlib.import_module(storage_plugin + storage.type)
    # s = module.Storage()
    # param = yield s.user_input_param()
    # param['proxy_id'] = param['proxy_id'][0] # should be selected by UI from proxy list
    # storage.path = yield s.upload_data('/bin/bash', param)

    # ipfs storage
    # storage.type = 'ipfs'

    # storage_plugin = "cpchain.storage_plugin."
    # module = importlib.import_module(storage_plugin + storage.type)
    # s = module.Storage()
    # param = yield s.user_input_param()
    # storage.path = yield s.upload_data('/bin/bash', param)

    # # S3 storage
    # storage.type = 's3'

    # storage_plugin = "cpchain.storage_plugin."
    # module = importlib.import_module(storage_plugin + storage.type)
    # s = module.Storage()
    # param = yield s.user_input_param()
    # storage.path = yield s.upload_data('/bin/bash', param)

    sign_message = SignMessage()
    sign_message.public_key = seller_public_key
    sign_message.data = message.SerializeToString()
    sign_message.signature = ECCipher.create_signature(
        seller_private_key,
        sign_message.data
        )

    proxy_list = yield pick_proxy()
    proxy_id = proxy_list[0] # should be selected by UI from proxy list

    if proxy_id:
        error, AES_key, urls = yield start_proxy_request(sign_message, proxy_id)

        if error:
            print(error)
        else:
            print(AES_key)
            print(urls)

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

    proxy_list = yield pick_proxy()
    proxy_id = proxy_list[0] # should be selected by UI from proxy list

    if proxy_id:
        error, AES_key, urls = yield start_proxy_request(sign_message, proxy_id)

        if error:
            print(error)
        else:
            print(AES_key)
            print(urls)

            file_name = urls[0].split('/')[3]
            file_dir = join_with_rc(config.wallet.download_dir)
            # create if not exists
            os.makedirs(file_dir, exist_ok=True)
            file_path = os.path.join(file_dir, file_name)

            yield download_proxy_file(urls[0], file_path)

seller_request()
buyer_request()

try:
    reactor.run()
except KeyboardInterrupt:
    pass
finally:
    pass
