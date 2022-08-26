# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tendermint/blocksync/types.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from tendermint.types import block_pb2 as tendermint_dot_types_dot_block__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n tendermint/blocksync/types.proto\x12\x14tendermint.blocksync\x1a\x1ctendermint/types/block.proto\"\x1e\n\x0c\x42lockRequest\x12\x0e\n\x06height\x18\x01 \x01(\x03\"!\n\x0fNoBlockResponse\x12\x0e\n\x06height\x18\x01 \x01(\x03\"7\n\rBlockResponse\x12&\n\x05\x62lock\x18\x01 \x01(\x0b\x32\x17.tendermint.types.Block\"\x0f\n\rStatusRequest\".\n\x0eStatusResponse\x12\x0e\n\x06height\x18\x01 \x01(\x03\x12\x0c\n\x04\x62\x61se\x18\x02 \x01(\x03\"\xd0\x02\n\x07Message\x12;\n\rblock_request\x18\x01 \x01(\x0b\x32\".tendermint.blocksync.BlockRequestH\x00\x12\x42\n\x11no_block_response\x18\x02 \x01(\x0b\x32%.tendermint.blocksync.NoBlockResponseH\x00\x12=\n\x0e\x62lock_response\x18\x03 \x01(\x0b\x32#.tendermint.blocksync.BlockResponseH\x00\x12=\n\x0estatus_request\x18\x04 \x01(\x0b\x32#.tendermint.blocksync.StatusRequestH\x00\x12?\n\x0fstatus_response\x18\x05 \x01(\x0b\x32$.tendermint.blocksync.StatusResponseH\x00\x42\x05\n\x03sumB=Z;github.com/tendermint/tendermint/proto/tendermint/blocksyncb\x06proto3')



_BLOCKREQUEST = DESCRIPTOR.message_types_by_name['BlockRequest']
_NOBLOCKRESPONSE = DESCRIPTOR.message_types_by_name['NoBlockResponse']
_BLOCKRESPONSE = DESCRIPTOR.message_types_by_name['BlockResponse']
_STATUSREQUEST = DESCRIPTOR.message_types_by_name['StatusRequest']
_STATUSRESPONSE = DESCRIPTOR.message_types_by_name['StatusResponse']
_MESSAGE = DESCRIPTOR.message_types_by_name['Message']
BlockRequest = _reflection.GeneratedProtocolMessageType('BlockRequest', (_message.Message,), {
  'DESCRIPTOR' : _BLOCKREQUEST,
  '__module__' : 'tendermint.blocksync.types_pb2'
  # @@protoc_insertion_point(class_scope:tendermint.blocksync.BlockRequest)
  })
_sym_db.RegisterMessage(BlockRequest)

NoBlockResponse = _reflection.GeneratedProtocolMessageType('NoBlockResponse', (_message.Message,), {
  'DESCRIPTOR' : _NOBLOCKRESPONSE,
  '__module__' : 'tendermint.blocksync.types_pb2'
  # @@protoc_insertion_point(class_scope:tendermint.blocksync.NoBlockResponse)
  })
_sym_db.RegisterMessage(NoBlockResponse)

BlockResponse = _reflection.GeneratedProtocolMessageType('BlockResponse', (_message.Message,), {
  'DESCRIPTOR' : _BLOCKRESPONSE,
  '__module__' : 'tendermint.blocksync.types_pb2'
  # @@protoc_insertion_point(class_scope:tendermint.blocksync.BlockResponse)
  })
_sym_db.RegisterMessage(BlockResponse)

StatusRequest = _reflection.GeneratedProtocolMessageType('StatusRequest', (_message.Message,), {
  'DESCRIPTOR' : _STATUSREQUEST,
  '__module__' : 'tendermint.blocksync.types_pb2'
  # @@protoc_insertion_point(class_scope:tendermint.blocksync.StatusRequest)
  })
_sym_db.RegisterMessage(StatusRequest)

StatusResponse = _reflection.GeneratedProtocolMessageType('StatusResponse', (_message.Message,), {
  'DESCRIPTOR' : _STATUSRESPONSE,
  '__module__' : 'tendermint.blocksync.types_pb2'
  # @@protoc_insertion_point(class_scope:tendermint.blocksync.StatusResponse)
  })
_sym_db.RegisterMessage(StatusResponse)

Message = _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), {
  'DESCRIPTOR' : _MESSAGE,
  '__module__' : 'tendermint.blocksync.types_pb2'
  # @@protoc_insertion_point(class_scope:tendermint.blocksync.Message)
  })
_sym_db.RegisterMessage(Message)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z;github.com/tendermint/tendermint/proto/tendermint/blocksync'
  _BLOCKREQUEST._serialized_start=88
  _BLOCKREQUEST._serialized_end=118
  _NOBLOCKRESPONSE._serialized_start=120
  _NOBLOCKRESPONSE._serialized_end=153
  _BLOCKRESPONSE._serialized_start=155
  _BLOCKRESPONSE._serialized_end=210
  _STATUSREQUEST._serialized_start=212
  _STATUSREQUEST._serialized_end=227
  _STATUSRESPONSE._serialized_start=229
  _STATUSRESPONSE._serialized_end=275
  _MESSAGE._serialized_start=278
  _MESSAGE._serialized_end=614
# @@protoc_insertion_point(module_scope)