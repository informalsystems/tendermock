from datetime import datetime
import grpc
import tendermint.abci.types_pb2 as atypes
import tendermint.abci.types_pb2_grpc as abci


if __name__ == '__main__':
    with grpc.insecure_channel('localhost:9091') as channel:
        stub = abci.ABCIApplicationStub(channel)
        request = atypes.RequestInitChain()
        # request.time = datetime.now().time()
        request.chain_id = "tendermock"

        validators = [
            atypes.ValidatorUpdate(pub_key = (5000 + i).to_bytes(2, byteorder="big"), power = i) for i in range(0, 5)
            ]

        request.validators = validators        

        response = stub.InitChain()