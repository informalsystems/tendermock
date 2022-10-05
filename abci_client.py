import asyncio
import base64
from dataclasses import dataclass
from email.mime import audio
import json
import sys
from typing import Dict, Optional
import grpc
from urllib import request
import init_chain
import begin_block
import end_block
from proto import tendermint_standalone
import proto.tendermint.abci as abci
import google.protobuf.timestamp_pb2 as times
import proto.cosmos.tx.v1beta1 as cosmostx
import proto.tendermint.types as ttypes
import proto.tendermint_standalone.state as ststate
import proto.tendermint_standalone.types as sttypes
import proto.tendermint_standalone.version as stversion
import logging
import typer
from google.protobuf.json_format import Parse
from grpclib.client import Channel
import betterproto

HOST = "0.0.0.0"
PORT = "26658"

# Path to the top-level directory of the protobuf-generated code, in dot notation.
# For example, foo.bar.proto
PROTO_PATH = "proto"

app = typer.Typer(pretty_exceptions_show_locals=False)


@dataclass(eq=False, repr=False)
class Any(betterproto.Message):
    type_url: str = betterproto.string_field(1)
    value: betterproto.Message = betterproto.message_field(2)

    def to_dict(
        self,
        casing: betterproto.Casing = betterproto.Casing.SNAKE,
        include_default_values: bool = False,
    ) -> Dict[str, object]:
        raw_dict = super().to_dict(casing, include_default_values)
        dict_: Dict[str, object] = {}
        type_url = casing("type_url").rstrip("_")  # type: ignore
        if type_url in raw_dict:
            dict_["@type"] = raw_dict[type_url]
        value = casing("value").rstrip("_")  # type: ignore
        dict_.update(raw_dict.get(value, {}))
        return dict_


def getClassForType(message: dict):

    # from https://stackoverflow.com/a/7281397
    def load_class(dottedpath):
        """Load a class from a module in dotted-path notation.

        E.g.: load_class("package.module.class").

        Based on recipe 16.3 from Python Cookbook, 2ed., by Alex Martelli,
        Anna Martelli Ravenscroft, and David Ascher (O'Reilly Media, 2005)

        """
        assert dottedpath is not None, "dottedpath must not be None"
        splitted_path = dottedpath.split(".")
        modulename = ".".join(splitted_path[:-1])
        classname = splitted_path[-1]
        try:
            try:
                module = __import__(modulename, globals(), locals(), [classname])
            except ValueError:  # Py < 2.5
                if not modulename:
                    module = __import__(
                        __name__.split(".")[0], globals(), locals(), [classname]
                    )
        except ImportError:
            # properly log the exception information and return None
            # to tell caller we did not succeed
            logging.exception(
                "Could not load class %s" " because an exception occurred", dottedpath
            )
            return None
        try:
            return getattr(module, classname)
        except AttributeError:
            logging.exception(
                "Could not load class %s" " because the class was not found", dottedpath
            )
            return None

    return load_class(PROTO_PATH + "." + message["@type"][1:])


def extractGenesisValidatorsFromGenesis(genesis_json):
    validators = [ttypes.Validator().from_dict(val_json) for val_json in genesis_json.get("validators", [])]

    return validators


def createAnyFromDict(message):
    type_url = "/" + message["@type"][1:]
    return Any(
        type_url=type_url,
        value=getClassForType(message)().from_dict(message).SerializeToString(),
    )


def createSignerInfo(info_dict):
    result = cosmostx.SignerInfo().from_dict(info_dict)
    result.public_key = createAnyFromDict(info_dict["public_key"])
    return result


@app.command()
def run(
    genesis_file: str = typer.Argument(...),
    trace_file: Optional[str] = typer.Argument(None),
):

    logging.basicConfig(filename="tendermock.log", level=logging.INFO)

    with (open(genesis_file, "r") as genesis_fileobject,):

        trace = []
        if trace_file is not None:
            with open(trace_file, "r") as trace_fileobject:
                trace = json.load(trace_fileobject)

        channel = Channel(host=HOST, port=PORT)
        stub = abci.AbciApplicationStub(channel)

        genesis_json = json.load(genesis_fileobject)

        genesisValidators = extractGenesisValidatorsFromGenesis(genesis_json)

        timestamp = times.Timestamp()

        initChainRequest = init_chain.RequestInitChainFactory().createRequestInitChain(
            genesis_json, genesisValidators, timestamp.GetCurrentTime()
        )

        state = ststate.State(
            version=ststate.Version(consensus=stversion.Consensus(block=1, app=0)),
            chain_id=genesis_json["chain_id"],
            initial_height=genesis_json["initial_height"],
            # last block
            last_block_height=0,
            last_block_id=sttypes.BlockId(),
            last_block_time=genesis_json["genesis_time"],
            # validators
            next_validators=ttypes.ValidatorSet().from_dict(
                {"validators": genesis_json.get("validators", [])}
            ),
            validators=ttypes.ValidatorSet().from_dict(
                {"validators": genesis_json.get("validators", [])}
            ),
            last_validators=ttypes.ValidatorSet(),
            last_height_validators_changed=genesis_json["initial_height"],
            # consensus params
            consensus_params=sttypes.ConsensusParams().from_dict(
                genesis_json["consensus_params"]
            ),
            last_height_consensus_params_changed=genesis_json["initial_height"],
            # app info
            app_hash=str.encode(json.dumps(genesis_json["app_state"])),
        )

        print(state.validators)

        logging.info(f"------> RequestInitChain:\n{initChainRequest}")

        response = asyncio.get_event_loop().run_until_complete(
            stub.init_chain(
                time=initChainRequest.time,
                chain_id=initChainRequest.chain_id,
                consensus_params=initChainRequest.consensus_params,
                validators=initChainRequest.validators,
                initial_height=initChainRequest.initial_height,
                app_state_bytes=initChainRequest.app_state_bytes,
            )
        )

        logging.info(f"------> ResponseInitChain:\n{response}")

        consensusParams = response.consensus_params
        validators = response.validators

        requestBeginBlockFactory = begin_block.RequestBeginBlockFactory(
            genesis_json["chain_id"]
        )
        requestEndBlockFactory = end_block.RequestEndBlockFactory()

        height = 1

        while height <= 4:
            print("Height=" + str(height))
            logging.info("Height=" + str(height))
            beginBlockRequest = requestBeginBlockFactory.createRequestBeginBlock(height)
            response = asyncio.get_event_loop().run_until_complete(
                stub.begin_block(
                    header=beginBlockRequest.header,
                    hash=beginBlockRequest.hash,
                    last_commit_info=beginBlockRequest.last_commit_info,
                    byzantine_validators=beginBlockRequest.byzantine_validators,
                )
            )

            logging.info(f"------> ResponseBeginBlock:\n{response}")

            # deliver transactions for current step
            # height starts at 1, but transactions for first block are at index 0
            tx_index = height - 1
            if tx_index < len(trace):
                tx_dict = trace[tx_index]
                logging.info("Sending transactions: " + str(tx_dict))

                tx_body = cosmostx.TxBody().from_dict(tx_dict["body"])

                tx_body.messages = [
                    createAnyFromDict(message)
                    for message in tx_dict["body"]["messages"]
                ]
                tx_auth_info = cosmostx.AuthInfo().from_dict(tx_dict["auth_info"])

                tx_auth_info.signer_infos = [
                    createSignerInfo(info)
                    for info in tx_dict["auth_info"]["signer_infos"]
                ]

                tx_protobuf = cosmostx.Tx().from_dict(tx_dict)
                tx_protobuf.body = tx_body
                tx_protobuf.auth_info = tx_auth_info

                response = asyncio.get_event_loop().run_until_complete(
                    stub.deliver_tx(tx=tx_protobuf.SerializeToString())
                )
                logging.info(f"------> ResponseDeliverTx:\n{response}")
            else:
                logging.info("Sending no transactions")

            endBlockRequest = requestEndBlockFactory.createRequestEndBlock(height)
            response = asyncio.get_event_loop().run_until_complete(
                stub.end_block(height=endBlockRequest.height)
            )
            logging.info(f"------> ResponseEndBlock:\n{response}")

            # commit needs nothing in the Request, but still has to provide an empty one
            response = asyncio.get_event_loop().run_until_complete(stub.commit())
            logging.info(f"------> ResponseCommit:\n{response}")

            # query info
            response = asyncio.get_event_loop().run_until_complete(stub.info())
            logging.info(f"------> ResponseInfo:\n{response}")

            height += 1
    channel.close()


def hexDump(data):
    linesHex = [data[i : i + 16].hex() for i in range(0, len(data), 16)]
    linesHexSpc = [
        " ".join([line[i : i + 2] for i in range(0, len(line), 2)]) for line in linesHex
    ]
    dataCharsDots = b"".join([bytes([i]) if 32 <= i <= 127 else b"." for i in data])
    linesChars = [
        dataCharsDots[i : i + 16].decode("ascii")
        for i in range(0, len(dataCharsDots), 16)
    ]
    assert len(linesHexSpc) == len(linesChars)
    formattedLines = [
        f"{i * 16:08x}  {linesHexSpc[i]:<{48}}  |{linesChars[i]}|"
        for i in range(len(linesHexSpc))
    ]
    print("\n".join(formattedLines))


if __name__ == "__main__":
    app()
