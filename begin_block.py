import json
import grpc
import tendermint.abci.types_pb2 as atypes
import tendermint.crypto.keys_pb2 as crypto
import tendermint.abci.types_pb2_grpc as abci
import tendermint.types.params_pb2 as params
import tendermint.types.types_pb2 as types
import google.protobuf.timestamp_pb2 as times
import google.protobuf.duration_pb2 as duration


class RequestBeginBlockFactory():
    def __init__(self, chain_id):
        self.chain_id = chain_id

    def createHeader(
        self,
        height
    ):
        header = types.Header(
            chain_id=self.chain_id,
            height=height
        )
        return header

    def createRequestBeginBlock(
        self,
        height
    ):
        header = self.createHeader(height)

        request = atypes.RequestBeginBlock(
            header=header
        )

        return request
