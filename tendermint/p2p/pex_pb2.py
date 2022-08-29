# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tendermint/p2p/pex.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from tendermint.p2p import types_pb2 as tendermint_dot_p2p_dot_types__pb2
from gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='tendermint/p2p/pex.proto',
  package='tendermint.p2p',
  syntax='proto3',
  serialized_options=_b('Z5github.com/tendermint/tendermint/proto/tendermint/p2p'),
  serialized_pb=_b('\n\x18tendermint/p2p/pex.proto\x12\x0etendermint.p2p\x1a\x1atendermint/p2p/types.proto\x1a\x14gogoproto/gogo.proto\"\x0c\n\nPexRequest\";\n\x08PexAddrs\x12/\n\x05\x61\x64\x64rs\x18\x01 \x03(\x0b\x32\x1a.tendermint.p2p.NetAddressB\x04\xc8\xde\x1f\x00\"r\n\x07Message\x12\x31\n\x0bpex_request\x18\x01 \x01(\x0b\x32\x1a.tendermint.p2p.PexRequestH\x00\x12-\n\tpex_addrs\x18\x02 \x01(\x0b\x32\x18.tendermint.p2p.PexAddrsH\x00\x42\x05\n\x03sumB7Z5github.com/tendermint/tendermint/proto/tendermint/p2pb\x06proto3')
  ,
  dependencies=[tendermint_dot_p2p_dot_types__pb2.DESCRIPTOR,gogoproto_dot_gogo__pb2.DESCRIPTOR,])




_PEXREQUEST = _descriptor.Descriptor(
  name='PexRequest',
  full_name='tendermint.p2p.PexRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=94,
  serialized_end=106,
)


_PEXADDRS = _descriptor.Descriptor(
  name='PexAddrs',
  full_name='tendermint.p2p.PexAddrs',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='addrs', full_name='tendermint.p2p.PexAddrs.addrs', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=_b('\310\336\037\000'), file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=108,
  serialized_end=167,
)


_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='tendermint.p2p.Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pex_request', full_name='tendermint.p2p.Message.pex_request', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pex_addrs', full_name='tendermint.p2p.Message.pex_addrs', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='sum', full_name='tendermint.p2p.Message.sum',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=169,
  serialized_end=283,
)

_PEXADDRS.fields_by_name['addrs'].message_type = tendermint_dot_p2p_dot_types__pb2._NETADDRESS
_MESSAGE.fields_by_name['pex_request'].message_type = _PEXREQUEST
_MESSAGE.fields_by_name['pex_addrs'].message_type = _PEXADDRS
_MESSAGE.oneofs_by_name['sum'].fields.append(
  _MESSAGE.fields_by_name['pex_request'])
_MESSAGE.fields_by_name['pex_request'].containing_oneof = _MESSAGE.oneofs_by_name['sum']
_MESSAGE.oneofs_by_name['sum'].fields.append(
  _MESSAGE.fields_by_name['pex_addrs'])
_MESSAGE.fields_by_name['pex_addrs'].containing_oneof = _MESSAGE.oneofs_by_name['sum']
DESCRIPTOR.message_types_by_name['PexRequest'] = _PEXREQUEST
DESCRIPTOR.message_types_by_name['PexAddrs'] = _PEXADDRS
DESCRIPTOR.message_types_by_name['Message'] = _MESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

PexRequest = _reflection.GeneratedProtocolMessageType('PexRequest', (_message.Message,), dict(
  DESCRIPTOR = _PEXREQUEST,
  __module__ = 'tendermint.p2p.pex_pb2'
  # @@protoc_insertion_point(class_scope:tendermint.p2p.PexRequest)
  ))
_sym_db.RegisterMessage(PexRequest)

PexAddrs = _reflection.GeneratedProtocolMessageType('PexAddrs', (_message.Message,), dict(
  DESCRIPTOR = _PEXADDRS,
  __module__ = 'tendermint.p2p.pex_pb2'
  # @@protoc_insertion_point(class_scope:tendermint.p2p.PexAddrs)
  ))
_sym_db.RegisterMessage(PexAddrs)

Message = _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGE,
  __module__ = 'tendermint.p2p.pex_pb2'
  # @@protoc_insertion_point(class_scope:tendermint.p2p.Message)
  ))
_sym_db.RegisterMessage(Message)


DESCRIPTOR._options = None
_PEXADDRS.fields_by_name['addrs']._options = None
# @@protoc_insertion_point(module_scope)
