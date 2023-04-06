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
    def __init__(self, application_addresses, genesis_file):
        self.application_addresses = application_addresses
        self.state = tstate.State()

        self.appStubs = {}

        print("Connecting to ABCI hosts")
        for address in self.application_addresses:
            host = address[0]
            port = address[1]
            print(f"> Connecting to ABCI on {host}:{port}")
            channel = Channel(host=host, port=port)
            self.appStubs[address] = abci.AbciApplicationStub(channel)

        if len(self.appStubs) == 0:
            raise Exception("Error: Should provide at least one application address")

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

            responses = []

            for addr in self.application_addresses:
                logging.info(f"initializing chain at {addr[0]}:{addr[1]}")
                logging.info(f"------> RequestInitChain:\n{initChainRequest}")

                response = asyncio.get_event_loop().run_until_complete(
                    self.appStubs.get(addr).init_chain(
                        time=initChainRequest.time,
                        chain_id=initChainRequest.chain_id,
                        consensus_params=initChainRequest.consensus_params,
                        validators=initChainRequest.validators,
                        initial_height=initChainRequest.initial_height,
                        app_state_bytes=initChainRequest.app_state_bytes,
                    )
                )

                logging.info(f"------> ResponseInitChain:\n{response}")
                responses.append(response)

            logging.info("using first response to update state")
            init_chain.applyResponseInitChain(self.state, responses[0])

    def getFirstAppStubAndAddress(self):
        return self.application_addresses[0], self.appStubs[self.application_addresses[0]]

    def checkTx(self, tx: bytes) -> abci.ResponseCheckTx:
        address, appStub = self.getFirstAppStubAndAddress()
        logging.info(f"checking transaction with app at {address}")
        response = asyncio.get_event_loop().run_until_complete(
            appStub.check_tx(tx=tx, type=abci.CheckTxType.NEW)
        )

        return response

    def _beginBlock(self, appStub, block: tmock.Block):
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
            appStub.begin_block(
                header=beginBlockRequest.header,
                hash=beginBlockRequest.hash,
                last_commit_info=beginBlockRequest.last_commit_info,
                byzantine_validators=beginBlockRequest.byzantine_validators,
            )
        )

        logging.info(f"------> ResponseBeginBlock:\n{response}")

    def _deliverTxs(self, appStub, txs: list[bytes]) -> list[abci.ResponseDeliverTx]:
        responses = [abci.ResponseDeliverTx()] * len(txs)
        for index, tx in enumerate(txs):
            logging.info("Sending transaction: " + str(tx))

            tx_bytes = tx.signed_tx

            response = asyncio.get_event_loop().run_until_complete(
                appStub.deliver_tx(tx=tx_bytes)
            )
            logging.info(f"------> ResponseDeliverTx:\n{response}")
            responses[index] = response
        return responses

    def _endBlock(self, appStub):
        response = asyncio.get_event_loop().run_until_complete(
            appStub.end_block(height=self.state.last_block_height + 1)
        )
        logging.info(f"------> ResponseEndBlock:\n{response}")

    def _commit(self, appStub):
        response = asyncio.get_event_loop().run_until_complete(appStub.commit())
        logging.info(f"------> ResponseCommit:\n{response}")

    # for block.txs[i], the ResponseDeliverTx is at position i of the returned list
    def runBlockForOneApp(
        self, appStub, block: tmock.Block
    ) -> list[abci.ResponseDeliverTx]:
        self._beginBlock(appStub, block)

        block_txs = block.txs
        if block_txs:
            responses = self._deliverTxs(appStub, block_txs)
        else:
            logging.info("Sending no transactions")
            responses = []

        self._endBlock(appStub)
        self._commit(appStub)

        return responses

    def runBlock(self, block: tmock.Block) -> dict[(str, str), list[abci.ResponseDeliverTx]]:
        """Runs a block on all connected apps.
        Returns a map of addresses to lists of responses: Each app responds to each Tx
        """
        appResponses = {}
        for addr in self.application_addresses:
            logging.info(f"running block for app at {addr[0]}:{addr[1]}")
            appStub = self.appStubs[addr]
            appResponses[addr] = self.runBlockForOneApp(appStub, block)
        self.state.last_block_height += 1

        return appResponses

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

    def abci_query(self, data, path, height, prove):
        logging.info(len(self.application_addresses))
        appAddr = self.application_addresses[0]
        appStub = self.appStubs.get(appAddr)
        print(appStub)
        response = asyncio.get_event_loop().run_until_complete(
            appStub.query(
                data=bytes.fromhex(data),
                path=path,
                height=int(height),
                prove=prove == "True",
            )
        )
        logging.info(response)
        return response
