from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.crypto import ECCipher
from cpchain.proxy.client import start_client, handle_proxy_response


def wallet_get_key_pair():

    # TODO: need to get private/public key pair from Ethereum interface
    private_key = b'\xa6\xf8_\xee\x1c\x85\xc5\x95\x8d@\x9e\xfa\x80\x7f\xb6\xe0\xb4u\x12\xb6\xdf\x00\xda4\x98\x8e\xaeR\x89~\xf6\xb5'
    public_key = b'0V0\x10\x06\x07*\x86H\xce=\x02\x01\x06\x05+\x81\x04\x00\n\x03B\x00\x04\\\xfd\xf7\xccD(\x1e\xce`|\x85\xad\xbc*,\x17h.Gj[_N\xadTa\xa9*\xa0x\xff\xb4as\xd1\x94\x9fN\xa3\xe2\xd1fX\xf6\xcf\x8e\xb9+\xab\x0f3\x81\x12\x91\xbdy\xbd\xec\xa6\rZ\x05:\x80'

    return private_key, public_key


def send_request_to_proxy(order_id, test_type):
    # TODO test_type param to be removed

    # TODO: need to get following data from market database
    seller_public_key = b'0V0\x10\x06\x07*\x86H\xce=\x02\x01\x06\x05+\x81\x04\x00\n\x03B\x00\x04\\\xfd\xf7\xccD(\x1e\xce`|\x85\xad\xbc*,\x17h.Gj[_N\xadTa\xa9*\xa0x\xff\xb4as\xd1\x94\x9fN\xa3\xe2\xd1fX\xf6\xcf\x8e\xb9+\xab\x0f3\x81\x12\x91\xbdy\xbd\xec\xa6\rZ\x05:\x80'
    buyer_public_key = b'0V0\x10\x06\x07*\x86H\xce=\x02\x01\x06\x05+\x81\x04\x00\n\x03B\x00\x04\\\xfd\xf7\xccD(\x1e\xce`|\x85\xad\xbc*,\x17h.Gj[_N\xadTa\xa9*\xa0x\xff\xb4as\xd1\x94\x9fN\xa3\xe2\xd1fX\xf6\xcf\x8e\xb9+\xab\x0f3\x81\x12\x91\xbdy\xbd\xec\xa6\rZ\x05:\x80'

    wallet_private_key, wallet_public_key = wallet_get_key_pair()

    if test_type == 'seller_data':

        # TODO: need to get following data from database
        AES_key = b'AES_key'
        storage_type = Message.Storage.IPFS
        ipfs_gateway = "192.168.0.132:5001"
        file_hash = b'QmT4kFS5gxzQZJwiDJQ66JLVGPpyTCF912bywYkpgyaPsD'
        market_hash = b'MARKET_HASH'

        message = Message()
        seller_data = message.seller_data
        message.type = Message.SELLER_DATA
        seller_data.order_id = order_id
        seller_data.seller_addr = seller_public_key
        seller_data.buyer_addr = buyer_public_key
        seller_data.market_hash = market_hash
        seller_data.AES_key = AES_key
        storage = seller_data.storage
        storage.type = storage_type
        ipfs = storage.ipfs
        ipfs.file_hash = file_hash
        ipfs.gateway = ipfs_gateway

        sign_message = SignMessage()
        sign_message.public_key = seller_public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.generate_signature(
                                wallet_private_key,
                                sign_message.data
                            )

        d = start_client(sign_message)

        # TODO: callback to be customized
        d.addBoth(handle_proxy_response)

    elif test_type == 'buyer_data':

        # TODO: need to get following data from database
        market_hash = b'MARKET_HASH'

        message = Message()
        buyer_data = message.buyer_data
        message.type = Message.BUYER_DATA
        buyer_data.order_id = order_id
        buyer_data.seller_addr = seller_public_key
        buyer_data.buyer_addr = buyer_public_key
        buyer_data.market_hash = market_hash

        sign_message = SignMessage()
        sign_message.public_key = buyer_public_key
        sign_message.data = message.SerializeToString()
        sign_message.signature = ECCipher.generate_signature(
                                wallet_private_key,
                                sign_message.data
                            )

        d = start_client(sign_message)

        # TODO: callback to be customized
        d.addBoth(handle_proxy_response)
