import json
import sys
from typing import Optional
import grpc
from urllib import request
import init_chain
import begin_block
import end_block
import tendermint.abci.types_pb2 as atypes
import tendermint.crypto.keys_pb2 as crypto
import tendermint.abci.types_pb2_grpc as abci
import tendermint.types.params_pb2 as params
import google.protobuf.timestamp_pb2 as times
import logging
import typer

address = "0.0.0.0"
port = "23456"

app = typer.Typer()


def extractValidatorsFromGenesis(genesis_json):
    gen_transactions = genesis_json["app_state"]["genutil"]["gen_txs"]

    gen_messages = [
        message for gen_tx in gen_transactions for message in gen_tx["body"]["messages"]
    ]
    validator_creations = [
        message
        for message in gen_messages
        if message["@type"] == "/cosmos.staking.v1beta1.MsgCreateValidator"
    ]

    validators = [
        {
            "address": msg["validator_address"],
            "pubkey": str.encode(msg["pubkey"]["key"]),
            "power": int(msg["value"]["amount"]),
        }
        for msg in validator_creations
    ]

    return validators


@app.command()
def run(
    genesis_file: str = typer.Argument(...),
    trace_file: Optional[str] = typer.Argument(None),
):
    logging.basicConfig(filename="tendermock.log", level=logging.INFO)

    with (
        grpc.insecure_channel(f"{address}:{port}") as channel,
        open(genesis_file, "r") as genesis_fileobject,
    ):
        trace = []
        if trace_file is not None:
            with open(trace_file, "r") as trace_fileobject:
                trace = json.load(trace_fileobject)

        stub = abci.ABCIApplicationStub(channel)

        with open(genesis_file, "r") as genesis_fileobject:
            genesis_json = json.load(genesis_fileobject)

            validators = extractValidatorsFromGenesis(genesis_json)

            timestamp = times.Timestamp()

            initChainRequest = (
                init_chain.RequestInitChainFactory().createRequestInitChain(
                    genesis_json, [], timestamp.GetCurrentTime()
                )
            )
            response = stub.InitChain(initChainRequest)

            requestBeginBlockFactory = begin_block.RequestBeginBlockFactory(
                genesis_json["chain_id"]
            )
            requestEndBlockFactory = end_block.RequestEndBlockFactory()

            height = 1

            while height <= 4:
                print("Height=" + str(height))
                logging.info("Height=" + str(height))
                beginBlockRequest = requestBeginBlockFactory.createRequestBeginBlock(
                    height
                )
                response = stub.BeginBlock(beginBlockRequest)

                logging.info(f"------> ResponseBeginBlock:\n{response}")

                # deliver transactions for current step
                # height starts at 1, but transactions for first block are at index 0
                tx_index = height - 1
                if tx_index < len(trace):
                    tx = trace[height - 1]
                    logging.info("Sending transactions: " + str(tx))

                    tx_bytes = str.encode(json.dumps(tx))

                    response = stub.DeliverTx(
                        atypes.RequestDeliverTx(tx=tx_bytes)
                    )
                    logging.info(f"------> ResponseEndBlock:\n{response}")
                else:
                    logging.info("Sending no transactions")

                endBlockRequest = requestEndBlockFactory.createRequestEndBlock(height)
                response = stub.EndBlock(endBlockRequest)
                logging.info(f"------> ResponseEndBlock:\n{response}")

                # commit needs nothing in the Request, but still has to provide an empty one
                response = stub.Commit(atypes.RequestCommit())
                logging.info(f"------> ResponseCommit:\n{response}")

                # query info
                response = stub.Info(atypes.RequestInfo())
                logging.info(f"------> ResponseInfo:\n{response}")

                height += 1


if __name__ == "__main__":
    app()
