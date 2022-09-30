import json
import grpc
import proto.tendermint.abci as atypes
import proto.tendermint.types as types
from validator import Validator


class RequestBeginBlockFactory:
    def __init__(self, chain_id):
        self.chain_id = chain_id

    def createHeader(self, height):
        header = types.Header(chain_id=self.chain_id, height=height)
        return header

    def createLastCommitInfo(self, consensus_rounds: int, validators: list[Validator]):
        pass

    def createRequestBeginBlock(self, height):
        header = self.createHeader(height)

        request = atypes.RequestBeginBlock(header=header)

        return request
