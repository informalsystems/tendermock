import json
from urllib import request
import grpc
import init_chain
import begin_block
import end_block
import tendermint.abci.types_pb2 as atypes
import tendermint.crypto.keys_pb2 as crypto
import tendermint.abci.types_pb2_grpc as abci
import tendermint.types.params_pb2 as params
import google.protobuf.timestamp_pb2 as times
import google.protobuf.duration_pb2 as duration

address = "0.0.0.0"
port = "23456"


class Node:
    def __init__(self, name, pubkey, balance, address):
        self.name = name,
        self.pubkey = pubkey
        self.balance = balance
        self.address = address


nodes = [
    # Node(name="node1",
    #      pubkey="GfeeC7hIIOerVkeZVwpjCs72cJ2tniAz1slhs8EhXHc",
    #      balance=5000000000,
    #      address="cosmosvaloper1jj2js4fj7xkc4e5av0lms6vdtl69s9wwj69vxm"),
    # Node(name="node1",
    #      pubkey="AhcDH3E9jPWPZLl6COi+WJ3cpEw0V4o5ESh5j7vR6uFC",
    #      balance=5000000000,
    #      address="cosmos1jj2js4fj7xkc4e5av0lms6vdtl69s9wwhw3e2g"),
    # Node(name="node2",
    #      pubkey="A95d1iMpxfAzSW0NXgeEov7afsejio8/ZkvzBxU0jrWv",
    #      balance=5000000000,
    #      address="cosmos134r9s82qv8fprz3y7fw5lv40yuvsh285vxev02")
]

if __name__ == '__main__':
    with grpc.insecure_channel(f"{address}:{port}") as channel:
        stub = abci.ABCIApplicationStub(channel)

        with open("genesis.json", 'r') as genesis_file:
            genesis_json = json.load(genesis_file)

            timestamp = times.Timestamp()

            initChainRequest = init_chain.RequestInitChainFactory().createRequestInitChain(
                genesis_json,
                nodes,
                timestamp.GetCurrentTime()
            )
            response = stub.InitChain(initChainRequest)

            requestBeginBlockFactory = begin_block.RequestBeginBlockFactory(
                genesis_json["chain_id"])
            requestEndBlockFactory = end_block.RequestEndBlockFactory()

            for height in range(1, 2):
                print("Height=" + str(height))
                beginBlockRequest = requestBeginBlockFactory.createRequestBeginBlock(
                    height)
                response = stub.BeginBlock(beginBlockRequest)

                endBlockRequest = requestEndBlockFactory.createRequestEndBlock(
                    height)
                response = stub.EndBlock(endBlockRequest)
