import json
import grpc
import proto.tendermint.abci as atypes


class RequestEndBlockFactory():
    def createRequestEndBlock(
        self,
        height
    ):
        request = atypes.RequestEndBlock(
            height=height
        )

        return request
