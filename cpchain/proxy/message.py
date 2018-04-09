from cpchain.proxy.msg.trade_msg_pb2 import Message, SignMessage
from cpchain.proxy.crypto import ECCipher

def message_sanity_check(message):

    if message and message.type:
        if message.type == Message.SELLER_DATA and \
            message.seller_data:
            seller_data = message.seller_data
            if seller_data.seller_addr and \
                seller_data.buyer_addr and \
                seller_data.market_hash and \
                seller_data.AES_key and \
                seller_data.storage:
                storage = seller_data.storage
                if storage.type:
                    if storage.type == Message.Storage.IPFS:
                        if storage.ipfs and \
                            storage.ipfs.gateway and \
                            storage.ipfs.file_hash:
                            return True
                    elif storage.type == Message.Storage.S3:
                        if storage.s3 and \
                            storage.s3.uri:
                            return True
        elif message.type == Message.BUYER_DATA and \
            message.buyer_data:
            buyer_data = message.buyer_data
            if buyer_data.seller_addr and \
                buyer_data.buyer_addr and \
                buyer_data.market_hash:
                return True

        elif message.type == Message.PROXY_REPLY and \
            message.proxy_reply:
            proxy_reply = message.proxy_reply
            if proxy_reply.error:
                return True
            elif proxy_reply.AES_key and \
                proxy_reply.file_uuid:
                return True

    return False

def sign_message_verify(sign_message):

    ec = ECCipher()

    ec.load_public_key(sign_message.public_key)
    ec.encode_signature(sign_message.signature)
    ec.load_sign_data(sign_message.data)

    if not ec.verify_signature():
        return False
    else:
        return True
