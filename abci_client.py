import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

import google.protobuf.timestamp_pb2 as times
import pandas
from grpclib.client import Channel

import init_chain
import proto.tendermint.abci as abci
import proto.tendermint.state as tstate
import proto.tendermint.types as ttypes
import proto.tendermint.version as tversion
import proto.tendermock as tmock
from utils import *


class ABCI_Client:
    def __init__(self, application_host, application_port, genesis_file):
        self.host = application_host
        self.port = application_port
        self.state = tstate.State()
        channel = Channel(host=self.host, port=self.port)
        self.stub = abci.AbciApplicationStub(channel)

        with open(genesis_file, "r") as genesis_fileobject:
            genesis_json = json.load(genesis_fileobject)

            genesisValidators = extractGenesisValidatorsFromGenesis(genesis_json)

            timestamp = times.Timestamp()

            initChainRequest = (
                init_chain.RequestInitChainFactory().createRequestInitChain(
                    genesis_json, genesisValidators, timestamp.GetCurrentTime()
                )
            )

            self.state = tstate.State(
                version=tstate.Version(consensus=tversion.Consensus(block=1, app=0)),
                chain_id=genesis_json["chain_id"],
                initial_height=genesis_json["initial_height"],
                # last block
                last_block_height=0,
                last_block_id=ttypes.BlockId(),
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
                consensus_params=ttypes.ConsensusParams().from_dict(
                    genesis_json["consensus_params"]
                ),
                last_height_consensus_params_changed=genesis_json["initial_height"],
                # app info
                app_hash=str.encode(json.dumps(genesis_json["app_state"])),
            )

            logging.info(f"------> RequestInitChain:\n{initChainRequest}")

            response = asyncio.get_event_loop().run_until_complete(
                self.stub.init_chain(
                    time=initChainRequest.time,
                    chain_id=initChainRequest.chain_id,
                    consensus_params=initChainRequest.consensus_params,
                    validators=initChainRequest.validators,
                    initial_height=initChainRequest.initial_height,
                    app_state_bytes=initChainRequest.app_state_bytes,
                )
            )

            logging.info(f"------> ResponseInitChain:\n{response}")

            init_chain.applyResponseInitChain(self.state, response)

    def _beginBlock(self, block: tmock.Block):
        # TODO: default logic, change this later to take the values from the given block
        signers = {val: True for val in self.state.last_validators.validators}

        beginBlockRequest = self._createRequestBeginBlock(
            height=self.state.last_block_height + 1,
            last_signers=signers,
            last_block_timestamp=self.state.last_block_time,
            byzantine_vals=[],
            proposer_address=self.state.last_validators.proposer.address,
            last_rounds_to_consensus=3,
        )

        response = asyncio.get_event_loop().run_until_complete(
            self.stub.begin_block(
                header=beginBlockRequest.header,
                hash=beginBlockRequest.hash,
                last_commit_info=beginBlockRequest.last_commit_info,
                byzantine_validators=beginBlockRequest.byzantine_validators,
            )
        )

        logging.info(f"------> ResponseBeginBlock:\n{response}")

    def _deliverTxs(self, txs: list[bytes]):
        for tx in txs:
            logging.info("Sending transaction: " + str(tx))

            tx_bytes = tx.signed_tx

            print(tx_bytes)

            response = asyncio.get_event_loop().run_until_complete(
                self.stub.deliver_tx(tx=tx_bytes)
            )
            print(response)
            logging.info(f"------> ResponseDeliverTx:\n{response}")

    def _endBlock(self):
        response = asyncio.get_event_loop().run_until_complete(
            self.stub.end_block(height=self.state.last_block_height + 1)
        )
        logging.info(f"------> ResponseEndBlock:\n{response}")

    def _commit(self):
        response = asyncio.get_event_loop().run_until_complete(self.stub.commit())
        logging.info(f"------> ResponseCommit:\n{response}")

    def runBlock(self, block: tmock.Block):
        self._beginBlock(block)

        block_txs = block.txs
        if block_txs:
            self._deliverTxs(block_txs)
        else:
            logging.info("Sending no transactions")

        self._endBlock()
        self._commit()

    def _createHeader(
        self,
        height: int,
        last_block_timestamp: datetime,
        byzantine_vals: ttypes.Evidence,
        proposer_address: bytes,
    ):
        # TODO: add hashes
        header = ttypes.Header(
            chain_id=self.state.chain_id,
            height=height,
            # time=last_block_timestamp,
            proposer_address=proposer_address,
        )
        return header

    def _createLastCommitInfo(self, consensus_rounds: int, last_commit_signers):
        if self.state.last_block_height == 0:
            # see https://github.com/tendermint/tendermint/blob/b9cdd0e28eb2c10f82a401b37c50dec0ab711c23/state/execution.go#L339
            # last commit info should be empty
            return abci.LastCommitInfo(consensus_rounds)
        else:
            return abci.LastCommitInfo(consensus_rounds)

    def _createRequestBeginBlock(
        self,
        height: int,
        # maps each validator to whether it signed or not. needs to include the whole validator set of the last block, both signing and nonsigning ones
        last_signers: dict[ttypes.Validator, bool],
        last_block_timestamp: datetime,
        byzantine_vals: list[ttypes.Evidence],
        proposer_address: bytes,
        last_rounds_to_consensus: int,
    ):
        header = self._createHeader(
            height=height,
            last_block_timestamp=last_block_timestamp,
            byzantine_vals=byzantine_vals,
            proposer_address=proposer_address,
        )

        last_commit_info = self._createLastCommitInfo(
            last_rounds_to_consensus, last_signers
        )

        request = abci.RequestBeginBlock(
            header=header,
            byzantine_validators=byzantine_vals,
            last_commit_info=last_commit_info,
        )

        return request
