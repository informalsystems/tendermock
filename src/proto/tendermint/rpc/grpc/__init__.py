# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: tendermint/rpc/grpc/types.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import Dict

import betterproto
from betterproto.grpc.grpclib_server import ServiceBase
import grpclib


@dataclass(eq=False, repr=False)
class RequestPing(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class RequestBroadcastTx(betterproto.Message):
    tx: bytes = betterproto.bytes_field(1)


@dataclass(eq=False, repr=False)
class ResponsePing(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class ResponseBroadcastTx(betterproto.Message):
    check_tx: "__abci__.ResponseCheckTx" = betterproto.message_field(1)
    deliver_tx: "__abci__.ResponseDeliverTx" = betterproto.message_field(2)


class BroadcastApiStub(betterproto.ServiceStub):
    async def ping(self) -> "ResponsePing":

        request = RequestPing()

        return await self._unary_unary(
            "/tendermint.rpc.grpc.BroadcastAPI/Ping", request, ResponsePing
        )

    async def broadcast_tx(self, *, tx: bytes = b"") -> "ResponseBroadcastTx":

        request = RequestBroadcastTx()
        request.tx = tx

        return await self._unary_unary(
            "/tendermint.rpc.grpc.BroadcastAPI/BroadcastTx",
            request,
            ResponseBroadcastTx,
        )


class BroadcastApiBase(ServiceBase):
    async def ping(self) -> "ResponsePing":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def broadcast_tx(self, tx: bytes) -> "ResponseBroadcastTx":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_ping(self, stream: grpclib.server.Stream) -> None:
        request = await stream.recv_message()

        request_kwargs = {}

        response = await self.ping(**request_kwargs)
        await stream.send_message(response)

    async def __rpc_broadcast_tx(self, stream: grpclib.server.Stream) -> None:
        request = await stream.recv_message()

        request_kwargs = {
            "tx": request.tx,
        }

        response = await self.broadcast_tx(**request_kwargs)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/tendermint.rpc.grpc.BroadcastAPI/Ping": grpclib.const.Handler(
                self.__rpc_ping,
                grpclib.const.Cardinality.UNARY_UNARY,
                RequestPing,
                ResponsePing,
            ),
            "/tendermint.rpc.grpc.BroadcastAPI/BroadcastTx": grpclib.const.Handler(
                self.__rpc_broadcast_tx,
                grpclib.const.Cardinality.UNARY_UNARY,
                RequestBroadcastTx,
                ResponseBroadcastTx,
            ),
        }


from ... import abci as __abci__
