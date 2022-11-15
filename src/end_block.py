import json
import grpc
import proto.tendermint.abci as abci


class RequestEndBlockFactory():
    def createRequestEndBlock(
        self,
        height
    ):
        request = abci.RequestEndBlock(
            height=height
        )

        return request
