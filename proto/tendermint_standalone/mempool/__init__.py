# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: tendermint/mempool/types.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import List

import betterproto
from betterproto.grpc.grpclib_server import ServiceBase


@dataclass(eq=False, repr=False)
class Txs(betterproto.Message):
    txs: List[bytes] = betterproto.bytes_field(1)


@dataclass(eq=False, repr=False)
class Message(betterproto.Message):
    txs: "Txs" = betterproto.message_field(1, group="sum")