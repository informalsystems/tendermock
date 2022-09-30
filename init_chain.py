import json
import grpc
import proto.tendermint.abci as abci
import proto.tendermint.crypto as crypto
import proto.tendermint.types as params
import google.protobuf.timestamp_pb2 as times
import google.protobuf.duration_pb2 as duration
from validator import Validator


class RequestInitChainFactory:
    def createAppstateBytes(self, genesis_json):
        app_state = genesis_json["app_state"]
        app_state_str = json.dumps(app_state)
        app_state_bytes = str.encode(app_state_str)
        return app_state_bytes

    def createConsensusParams(self, genesis_json):
        genesis_params = genesis_json["consensus_params"]
        block_params = abci.BlockParams(
            max_bytes=int(genesis_params["block"]["max_bytes"]),
            max_gas=int(genesis_params["block"]["max_gas"]),
        )

        evidence_params = params.EvidenceParams(
            max_age_num_blocks=int(genesis_params["evidence"]["max_age_num_blocks"]),
            max_age_duration=duration.Duration(
                seconds=int(
                    # convert nanos to seconds
                    int(genesis_params["evidence"]["max_age_duration"])
                    / 1e9
                )
            ).ToTimedelta(),
            max_bytes=int(genesis_params["evidence"]["max_bytes"]),
        )

        validator_params = params.ValidatorParams(
            pub_key_types=genesis_params["validator"]["pub_key_types"]
        )

        version_params = params.VersionParams()

        consensus_params = abci.ConsensusParams(
            block=block_params,
            evidence=evidence_params,
            validator=validator_params,
            version=version_params,
        )

        return consensus_params

    def createValidatorList(self, validators: list[Validator]):
        validator_updates = [
            abci.ValidatorUpdate(
                pub_key=crypto.PublicKey(ed25519=validator.pubkey),
                power=validator.power,
            )
            for validator in validators
        ]
        return validator_updates

    def createRequestInitChain(self, genesis_json, validators, time):
        # request.time = datetime.now().time()
        validator_updates = self.createValidatorList(validators)

        app_state_bytes = self.createAppstateBytes(genesis_json)

        consensus_params = self.createConsensusParams(genesis_json)

        request = abci.RequestInitChain(
            time=time,
            chain_id=genesis_json["chain_id"],
            consensus_params=consensus_params,
            app_state_bytes=app_state_bytes,
            initial_height=int(genesis_json["initial_height"]),
            validators=validator_updates,
        )

        return request
