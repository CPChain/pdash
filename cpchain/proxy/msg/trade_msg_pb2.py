# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: trade_msg.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='trade_msg.proto',
  package='cpchain',
  syntax='proto3',
  serialized_pb=_b('\n\x0ftrade_msg.proto\x12\x07\x63pchain\"\xd1\x06\n\x07Message\x12*\n\x04type\x18\x01 \x01(\x0e\x32\x1c.cpchain.Message.MessageType\x12\x30\n\x0bseller_data\x18\x02 \x01(\x0b\x32\x1b.cpchain.Message.SellerData\x12.\n\nbuyer_data\x18\x03 \x01(\x0b\x32\x1a.cpchain.Message.BuyerData\x12\x30\n\x0bproxy_reply\x18\x04 \x01(\x0b\x32\x1b.cpchain.Message.ProxyReply\x1a\xa1\x02\n\x07Storage\x12\x32\n\x04type\x18\x01 \x01(\x0e\x32$.cpchain.Message.Storage.StorageType\x12\x33\n\x04ipfs\x18\x02 \x01(\x0b\x32%.cpchain.Message.Storage.IPFS_Storage\x12/\n\x02s3\x18\x03 \x01(\x0b\x32#.cpchain.Message.Storage.S3_Storage\x1a\x32\n\x0cIPFS_Storage\x12\x11\n\tfile_hash\x18\x01 \x01(\x0c\x12\x0f\n\x07gateway\x18\x02 \x01(\t\x1a\x19\n\nS3_Storage\x12\x0b\n\x03uri\x18\x01 \x01(\t\"-\n\x0bStorageType\x12\x0c\n\x08RESERVED\x10\x00\x12\x08\n\x04IPFS\x10\x01\x12\x06\n\x02S3\x10\x02\x1a\x86\x01\n\nSellerData\x12\x13\n\x0bseller_addr\x18\x01 \x01(\x0c\x12\x12\n\nbuyer_addr\x18\x02 \x01(\x0c\x12\x13\n\x0bmarket_hash\x18\x03 \x01(\x0c\x12\x0f\n\x07\x41\x45S_key\x18\x04 \x01(\x0c\x12)\n\x07storage\x18\x05 \x01(\x0b\x32\x18.cpchain.Message.Storage\x1aI\n\tBuyerData\x12\x13\n\x0bseller_addr\x18\x01 \x01(\x0c\x12\x12\n\nbuyer_addr\x18\x02 \x01(\x0c\x12\x13\n\x0bmarket_hash\x18\x03 \x01(\x0c\x1a?\n\nProxyReply\x12\r\n\x05\x65rror\x18\x01 \x01(\t\x12\x0f\n\x07\x41\x45S_key\x18\x02 \x01(\x0c\x12\x11\n\tfile_uuid\x18\x03 \x01(\t\"M\n\x0bMessageType\x12\x0c\n\x08RESERVED\x10\x00\x12\x0f\n\x0bSELLER_DATA\x10\x01\x12\x0e\n\nBUYER_DATA\x10\x02\x12\x0f\n\x0bPROXY_REPLY\x10\x03\"B\n\x0bSignMessage\x12\x12\n\npublic_key\x18\x01 \x01(\x0c\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\x12\x11\n\tsignature\x18\x03 \x01(\x0c\x62\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_MESSAGE_STORAGE_STORAGETYPE = _descriptor.EnumDescriptor(
  name='StorageType',
  full_name='cpchain.Message.Storage.StorageType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='RESERVED', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='IPFS', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='S3', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=477,
  serialized_end=522,
)
_sym_db.RegisterEnumDescriptor(_MESSAGE_STORAGE_STORAGETYPE)

_MESSAGE_MESSAGETYPE = _descriptor.EnumDescriptor(
  name='MessageType',
  full_name='cpchain.Message.MessageType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='RESERVED', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SELLER_DATA', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BUYER_DATA', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PROXY_REPLY', index=3, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=801,
  serialized_end=878,
)
_sym_db.RegisterEnumDescriptor(_MESSAGE_MESSAGETYPE)


_MESSAGE_STORAGE_IPFS_STORAGE = _descriptor.Descriptor(
  name='IPFS_Storage',
  full_name='cpchain.Message.Storage.IPFS_Storage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='file_hash', full_name='cpchain.Message.Storage.IPFS_Storage.file_hash', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gateway', full_name='cpchain.Message.Storage.IPFS_Storage.gateway', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=398,
  serialized_end=448,
)

_MESSAGE_STORAGE_S3_STORAGE = _descriptor.Descriptor(
  name='S3_Storage',
  full_name='cpchain.Message.Storage.S3_Storage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uri', full_name='cpchain.Message.Storage.S3_Storage.uri', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=450,
  serialized_end=475,
)

_MESSAGE_STORAGE = _descriptor.Descriptor(
  name='Storage',
  full_name='cpchain.Message.Storage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='cpchain.Message.Storage.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ipfs', full_name='cpchain.Message.Storage.ipfs', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='s3', full_name='cpchain.Message.Storage.s3', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_MESSAGE_STORAGE_IPFS_STORAGE, _MESSAGE_STORAGE_S3_STORAGE, ],
  enum_types=[
    _MESSAGE_STORAGE_STORAGETYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=233,
  serialized_end=522,
)

_MESSAGE_SELLERDATA = _descriptor.Descriptor(
  name='SellerData',
  full_name='cpchain.Message.SellerData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='seller_addr', full_name='cpchain.Message.SellerData.seller_addr', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='buyer_addr', full_name='cpchain.Message.SellerData.buyer_addr', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='market_hash', full_name='cpchain.Message.SellerData.market_hash', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='AES_key', full_name='cpchain.Message.SellerData.AES_key', index=3,
      number=4, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='storage', full_name='cpchain.Message.SellerData.storage', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=525,
  serialized_end=659,
)

_MESSAGE_BUYERDATA = _descriptor.Descriptor(
  name='BuyerData',
  full_name='cpchain.Message.BuyerData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='seller_addr', full_name='cpchain.Message.BuyerData.seller_addr', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='buyer_addr', full_name='cpchain.Message.BuyerData.buyer_addr', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='market_hash', full_name='cpchain.Message.BuyerData.market_hash', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=661,
  serialized_end=734,
)

_MESSAGE_PROXYREPLY = _descriptor.Descriptor(
  name='ProxyReply',
  full_name='cpchain.Message.ProxyReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='error', full_name='cpchain.Message.ProxyReply.error', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='AES_key', full_name='cpchain.Message.ProxyReply.AES_key', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='file_uuid', full_name='cpchain.Message.ProxyReply.file_uuid', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=736,
  serialized_end=799,
)

_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='cpchain.Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='cpchain.Message.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='seller_data', full_name='cpchain.Message.seller_data', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='buyer_data', full_name='cpchain.Message.buyer_data', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='proxy_reply', full_name='cpchain.Message.proxy_reply', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_MESSAGE_STORAGE, _MESSAGE_SELLERDATA, _MESSAGE_BUYERDATA, _MESSAGE_PROXYREPLY, ],
  enum_types=[
    _MESSAGE_MESSAGETYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=29,
  serialized_end=878,
)


_SIGNMESSAGE = _descriptor.Descriptor(
  name='SignMessage',
  full_name='cpchain.SignMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='public_key', full_name='cpchain.SignMessage.public_key', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data', full_name='cpchain.SignMessage.data', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='signature', full_name='cpchain.SignMessage.signature', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=880,
  serialized_end=946,
)

_MESSAGE_STORAGE_IPFS_STORAGE.containing_type = _MESSAGE_STORAGE
_MESSAGE_STORAGE_S3_STORAGE.containing_type = _MESSAGE_STORAGE
_MESSAGE_STORAGE.fields_by_name['type'].enum_type = _MESSAGE_STORAGE_STORAGETYPE
_MESSAGE_STORAGE.fields_by_name['ipfs'].message_type = _MESSAGE_STORAGE_IPFS_STORAGE
_MESSAGE_STORAGE.fields_by_name['s3'].message_type = _MESSAGE_STORAGE_S3_STORAGE
_MESSAGE_STORAGE.containing_type = _MESSAGE
_MESSAGE_STORAGE_STORAGETYPE.containing_type = _MESSAGE_STORAGE
_MESSAGE_SELLERDATA.fields_by_name['storage'].message_type = _MESSAGE_STORAGE
_MESSAGE_SELLERDATA.containing_type = _MESSAGE
_MESSAGE_BUYERDATA.containing_type = _MESSAGE
_MESSAGE_PROXYREPLY.containing_type = _MESSAGE
_MESSAGE.fields_by_name['type'].enum_type = _MESSAGE_MESSAGETYPE
_MESSAGE.fields_by_name['seller_data'].message_type = _MESSAGE_SELLERDATA
_MESSAGE.fields_by_name['buyer_data'].message_type = _MESSAGE_BUYERDATA
_MESSAGE.fields_by_name['proxy_reply'].message_type = _MESSAGE_PROXYREPLY
_MESSAGE_MESSAGETYPE.containing_type = _MESSAGE
DESCRIPTOR.message_types_by_name['Message'] = _MESSAGE
DESCRIPTOR.message_types_by_name['SignMessage'] = _SIGNMESSAGE

Message = _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), dict(

  Storage = _reflection.GeneratedProtocolMessageType('Storage', (_message.Message,), dict(

    IPFS_Storage = _reflection.GeneratedProtocolMessageType('IPFS_Storage', (_message.Message,), dict(
      DESCRIPTOR = _MESSAGE_STORAGE_IPFS_STORAGE,
      __module__ = 'trade_msg_pb2'
      # @@protoc_insertion_point(class_scope:cpchain.Message.Storage.IPFS_Storage)
      ))
    ,

    S3_Storage = _reflection.GeneratedProtocolMessageType('S3_Storage', (_message.Message,), dict(
      DESCRIPTOR = _MESSAGE_STORAGE_S3_STORAGE,
      __module__ = 'trade_msg_pb2'
      # @@protoc_insertion_point(class_scope:cpchain.Message.Storage.S3_Storage)
      ))
    ,
    DESCRIPTOR = _MESSAGE_STORAGE,
    __module__ = 'trade_msg_pb2'
    # @@protoc_insertion_point(class_scope:cpchain.Message.Storage)
    ))
  ,

  SellerData = _reflection.GeneratedProtocolMessageType('SellerData', (_message.Message,), dict(
    DESCRIPTOR = _MESSAGE_SELLERDATA,
    __module__ = 'trade_msg_pb2'
    # @@protoc_insertion_point(class_scope:cpchain.Message.SellerData)
    ))
  ,

  BuyerData = _reflection.GeneratedProtocolMessageType('BuyerData', (_message.Message,), dict(
    DESCRIPTOR = _MESSAGE_BUYERDATA,
    __module__ = 'trade_msg_pb2'
    # @@protoc_insertion_point(class_scope:cpchain.Message.BuyerData)
    ))
  ,

  ProxyReply = _reflection.GeneratedProtocolMessageType('ProxyReply', (_message.Message,), dict(
    DESCRIPTOR = _MESSAGE_PROXYREPLY,
    __module__ = 'trade_msg_pb2'
    # @@protoc_insertion_point(class_scope:cpchain.Message.ProxyReply)
    ))
  ,
  DESCRIPTOR = _MESSAGE,
  __module__ = 'trade_msg_pb2'
  # @@protoc_insertion_point(class_scope:cpchain.Message)
  ))
_sym_db.RegisterMessage(Message)
_sym_db.RegisterMessage(Message.Storage)
_sym_db.RegisterMessage(Message.Storage.IPFS_Storage)
_sym_db.RegisterMessage(Message.Storage.S3_Storage)
_sym_db.RegisterMessage(Message.SellerData)
_sym_db.RegisterMessage(Message.BuyerData)
_sym_db.RegisterMessage(Message.ProxyReply)

SignMessage = _reflection.GeneratedProtocolMessageType('SignMessage', (_message.Message,), dict(
  DESCRIPTOR = _SIGNMESSAGE,
  __module__ = 'trade_msg_pb2'
  # @@protoc_insertion_point(class_scope:cpchain.SignMessage)
  ))
_sym_db.RegisterMessage(SignMessage)


# @@protoc_insertion_point(module_scope)
