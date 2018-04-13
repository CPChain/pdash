from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.crypto import ECCipher
from cpchain.proxy.client import start_client, handle_proxy_response


def wallet_get_key_pair(test_type):
    # TODO: test_type param to be removed

    # TODO: need to get private/public key pair from Ethereum interface
    if test_type == 'seller_data':
        private_key = b'0\x81\xec0W\x06\t*\x86H\x86\xf7\r\x01\x05\r0J0)\x06\t*\x86H\x86\xf7\r\x01\x05\x0c0\x1c\x04\x08\xc7\x05\xb9\xa9\xbew\xdf$\x02\x02\x08\x000\x0c\x06\x08*\x86H\x86\xf7\r\x02\t\x05\x000\x1d\x06\t`\x86H\x01e\x03\x04\x01*\x04\x10P\xf8\t\xf3\x1eL\xd5\x1c4H\x9e2\x8b\xcbv0\x04\x81\x90V\xfe^\xcf"j\x86\x1a\xf1_\xab\x96\xd6{;{K3o~\xe9\xc4\xc5\xbb\xd2\xe2\xbeI3\x08\xc1\xeb\xdbuQJ\xd3\xfat\xb4W;60d\nAy\xe0\x08\x10\xeb\x9bM\xb4\xad\xe0e\xd1\xd5\xafX\xd5\x83\xb6\xc6\'\x82\xd2\x8e\xd0\x08y\xc1w\x19\xf8P>\xf9\xe4\x95\xe3\x17\x82\xce\xb9\xdb?\xdc\x10\xa5Z\xd3\xaef\x0e\x90\x8d\x7fkA\r\xaaD\x1d\xde\xc7J\x86e\xee\x9d\x1b\xb0\x16W\xb7\xab\xc35X\xae\x16\xad\xb5\r\x82\x91Djt"\xed#\xcc\xde\xe1\xa4\xe9Ww\xf6\x87'
        public_key = b"0V0\x10\x06\x07*\x86H\xce=\x02\x01\x06\x05+\x81\x04\x00\n\x03B\x00\x04\xf1\xf7Y\xf3fY\xad\x9c\xdf\xaa&\x8b\x86\xca\xcf$E5Hu\xd8t?+=\x97m\x07D\xbe\r\xa9\xcd\x05^N%O\x91'\xb0\x1doo'K6\x94^\xae#hj\xbd&\x94\x8b\xa6/\xa0\x1aU\x9c\xdd"
    elif test_type == 'buyer_data':
        private_key = b'0\x81\xec0W\x06\t*\x86H\x86\xf7\r\x01\x05\r0J0)\x06\t*\x86H\x86\xf7\r\x01\x05\x0c0\x1c\x04\x08\x85c\xfe}\x89?\xd2k\x02\x02\x08\x000\x0c\x06\x08*\x86H\x86\xf7\r\x02\t\x05\x000\x1d\x06\t`\x86H\x01e\x03\x04\x01*\x04\x10\x10\xdf\x02\x0e\xe6\xdcy\xce\x16\xbb\x8e\x03\xc9\xa6\xe9\xf1\x04\x81\x90\xd1\xfd\x0e\x01\'\xeb\x04\xb6\tHi\x14\x0bN\xabp"$\x04\xcc;\xadh\x07-\xc9\xd3\xe8\xc4\xcb\x8d\xfc\x10\xd0$\xab <#5\n\x1b\xe9\xafL\x8b\x06\xb2\x99\xab\x8a-\xed\x90\xf4\xd7\x99\x10\xf6\xc9\\m#\xdeqW\xc3 \xff\xd4d`\n\xedm\x98Mig\xdc\xac\x87A\x9f\xe4\xef,\xcf\xc9\xec\xc2|\x85M\xc9v7(\x00\x08\xdb\xeeq\xa0\xf8:\xde\xa9sV\xa9\x0fs\x80d&3\\f\x94\xd0\x19\xfd\x9cJ\xa5W\x86\x0f\xd88\xff\x1d]\xd6\xb5E\xa1Z\xf7\x15\x81,\x8d'
        public_key = b'0V0\x10\x06\x07*\x86H\xce=\x02\x01\x06\x05+\x81\x04\x00\n\x03B\x00\x04\x07\xd9x\x05=X/\x05\xbe;\x17\xac*\x15:\xdf-\x8bM\x10^\xcaz\xee\xb3\x06@\xc7\x8b\xe4z\xb1\xfc\x19h\xbc\x17\xf0\xa7\xe2\x87\x90\x1c\r\x07\xe4\xdf\x0e\xeb\x861-|}}\x9a\x1c\x00\x87\x93H\xa0\x8b#'

    return private_key, public_key


def send_request_to_proxy(market_hash, test_type):
    # TODO test_type param to be removed

    # TODO: need to get following data from market database
    seller_public_key = b"0V0\x10\x06\x07*\x86H\xce=\x02\x01\x06\x05+\x81\x04\x00\n\x03B\x00\x04\xf1\xf7Y\xf3fY\xad\x9c\xdf\xaa&\x8b\x86\xca\xcf$E5Hu\xd8t?+=\x97m\x07D\xbe\r\xa9\xcd\x05^N%O\x91'\xb0\x1doo'K6\x94^\xae#hj\xbd&\x94\x8b\xa6/\xa0\x1aU\x9c\xdd"
    buyer_public_key = b'0V0\x10\x06\x07*\x86H\xce=\x02\x01\x06\x05+\x81\x04\x00\n\x03B\x00\x04\x07\xd9x\x05=X/\x05\xbe;\x17\xac*\x15:\xdf-\x8bM\x10^\xcaz\xee\xb3\x06@\xc7\x8b\xe4z\xb1\xfc\x19h\xbc\x17\xf0\xa7\xe2\x87\x90\x1c\r\x07\xe4\xdf\x0e\xeb\x861-|}}\x9a\x1c\x00\x87\x93H\xa0\x8b#'

    wallet_private_key, wallet_public_key = wallet_get_key_pair(test_type)

    if wallet_public_key == seller_public_key:

        # TODO: need to get following data from market database
        AES_key = b'AES_key'
        storage_type = Message.Storage.IPFS
        ipfs_gateway = "192.168.0.132:5001"
        file_hash = b'QmT4kFS5gxzQZJwiDJQ66JLVGPpyTCF912bywYkpgyaPsD'

        message = Message()
        seller_data = message.seller_data
        message.type = Message.SELLER_DATA
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

    elif wallet_public_key == buyer_public_key:
        message = Message()
        buyer_data = message.buyer_data
        message.type = Message.BUYER_DATA
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
