import json
import grpc
import tendermint.abci.types_pb2 as atypes
import tendermint.crypto.keys_pb2 as crypto
import tendermint.abci.types_pb2_grpc as abci
import tendermint.types.params_pb2 as params
import tendermint.types.types_pb2 as types
import google.protobuf.timestamp_pb2 as times
import google.protobuf.duration_pb2 as duration


class RequestEndBlockFactory():
    def createRequestEndBlock(
        self,
        height
    ):
        request = atypes.RequestEndBlock(
            height=height
        )

        return request
