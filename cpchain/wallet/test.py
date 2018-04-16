from cpchain.wallet import proxy_request
from cpchain import crypto

market_hash = '5rdXcW+05mSPmgjLFLmLTiBZmCxzTbdQnPTEriTY3/4='.encode("utf-8")

message = Message()
seller_data = message.seller_data
message.type = Message.SELLER_DATA
seller_data.seller_addr = crypto.Encoder.str_to_base64_byte(market_client.pub_key)
seller_data.buyer_addr = crypto.Encoder.str_to_base64_byte(market_client.pub_key)
seller_data.market_hash = market_hash
seller_data.AES_key = b'AES_key'
storage = seller_data.storage
storage.type = Message.Storage.IPFS
ipfs = storage.ipfs
ipfs.file_hash = b'QmT4kFS5gxzQZJwiDJQ66JLVGPpyTCF912bywYkpgyaPsD'
ipfs.gateway = "192.168.0.132:5001"

sign_message = SignMessage()
sign_message.public_key = crypto.Encoder.str_to_base64_byte(market_client.pub_key)
sign_message.data = message.SerializeToString()
sign_message.signature = crypto.ECCipher.generate_signature(
    crypto.Encoder.str_to_base64_byte(market_client.priv_key),
    sign_message.data
)

d = start_client(sign_message)
d.addBoth(self.callback_func_example)

def callback_func_example(self):
    print('success') 