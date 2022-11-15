# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: tendermock/traces.proto
# plugin: python-betterproto
from dataclasses import dataclass
from datetime import timedelta
from typing import List

import betterproto
from betterproto.grpc.grpclib_server import ServiceBase


@dataclass(eq=False, repr=False)
class Trace(betterproto.Message):
    blocks: List["Block"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class Block(betterproto.Message):
    txs: List["Transaction"] = betterproto.message_field(1)
    signers: "Signers" = betterproto.message_field(2)
    time_since_last_block: timedelta = betterproto.message_field(3)
    byzantine_vals: List["_tendermint_types__.Evidence"] = betterproto.message_field(4)
    # TODO: this is not what Tendermint does... does it need to be? if not given,
    # one validator is chosen at random, weighted by voting power
    proposer: "Validator" = betterproto.message_field(5)
    rounds: int = betterproto.int64_field(6)


@dataclass(eq=False, repr=False)
class Transaction(betterproto.Message):
    signed_tx: bytes = betterproto.bytes_field(1)


@dataclass(eq=False, repr=False)
class Validator(betterproto.Message):
    address: bytes = betterproto.bytes_field(1)


@dataclass(eq=False, repr=False)
class Signers(betterproto.Message):
    vals: List["Validator"] = betterproto.message_field(1)


from ..tendermint import types as _tendermint_types__