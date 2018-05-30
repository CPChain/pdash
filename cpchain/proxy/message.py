from cpchain.proxy.msg.trade_msg_pb2 import Message
from cpchain.crypto import ECCipher

def message_sanity_check(message):

    if not message or not message.type:
        return False

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
                        storage.s3.bucket and \
                        storage.s3.key:
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
            proxy_reply.file_uri:
            return True

    return False

def sign_message_verify(sign_message):

    try:
        public_key = ECCipher.create_public_key(sign_message.public_key)

        valid = ECCipher.verify_sign(
            public_key,
            sign_message.signature,
            sign_message.data
            )
    except:
        return False

    else:
        return valid

def is_address_from_key(addr, public_key):
    public_key = ECCipher.create_public_key(public_key)
    public_addr = ECCipher.get_address_from_public_key(public_key)

    return addr == public_addr
