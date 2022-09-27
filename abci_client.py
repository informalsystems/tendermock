import json
import sys
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
import logging

address = "0.0.0.0"
port = "23456"

def extractValidatorsFromGenesis(genesis_json):
    gen_transactions = genesis_json["app_state"]["genutil"]["gen_txs"]

    gen_messages = [message for gen_tx in gen_transactions for message in gen_tx["body"]["messages"]]
    validator_creations = [message for message in gen_messages 
        if message["@type"] == "/cosmos.staking.v1beta1.MsgCreateValidator"]

    validators = [
        {
        "address": msg["validator_address"], 
        "pubkey": str.encode(msg["pubkey"]["key"]),
        "power": int(msg["value"]["amount"])
        }
        for msg in validator_creations]
    
    return validators

if __name__ == '__main__':
    
    logging.basicConfig(filename='tendermock.log', level=logging.INFO)



    with grpc.insecure_channel(f"{address}:{port}") as channel:
        stub = abci.ABCIApplicationStub(channel)

        with open("genesis.json", 'r') as genesis_file:
            genesis_json = json.load(genesis_file)

            validators = extractValidatorsFromGenesis(genesis_json)

            timestamp = times.Timestamp()

            initChainRequest = init_chain.RequestInitChainFactory().createRequestInitChain(
                genesis_json,
                validators,
                timestamp.GetCurrentTime()
            )
            response = stub.InitChain(initChainRequest)

            requestBeginBlockFactory = begin_block.RequestBeginBlockFactory(
                genesis_json["chain_id"])
            requestEndBlockFactory = end_block.RequestEndBlockFactory()

            height = 1

            while height <= 10000000:
                print("Height=" + str(height))
                beginBlockRequest = requestBeginBlockFactory.createRequestBeginBlock(
                    height)
                response = stub.BeginBlock(beginBlockRequest)
                
                logging.info(f"------> ResponseBeginBlock:\n{response}")

                endBlockRequest = requestEndBlockFactory.createRequestEndBlock(
                    height)
                response = stub.EndBlock(endBlockRequest)
                logging.info(f"------> ResponseEndBlock:\n{response}")

                # commit needs nothing in the Request, but still has to provide an empty one
                response = stub.Commit(atypes.RequestCommit())
                logging.info(f"------> ResponseCommit:\n{response}")

                height+=1


