import grpc
import tendermint.abci.types_pb2_grpc as abci


if __name__ == '__main__':
    with grpc.insecure_channel('localhost:9091') as channel:
        stub = abci.ABCIApplicationStub(channel)