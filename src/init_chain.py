import json
import proto.tendermint.types as ttypes
import proto.tendermint.crypto as tcrypto
import proto.tendermint.state as tstate
import proto.tendermint.abci as abci


class RequestInitChainFactory:
    def createAppstateBytes(self, genesis_json):
        app_state = genesis_json["app_state"]
        app_state_str = json.dumps(app_state)
        app_state_bytes = str.encode(app_state_str)
        return app_state_bytes

    def createConsensusParams(self, genesis_json):
        genesis_params = genesis_json["consensus_params"]

        # times are read as seconds, but should be nanoseconds. seems its a difference in how Go vs Python handle this
        genesis_params["evidence"]["max_age_duration"] = str(
            int(genesis_params["evidence"]["max_age_duration"])
        )

        print(genesis_params)

        consensus_params = ttypes.ConsensusParams().from_dict(genesis_params)

        return consensus_params

    def createValidatorList(self, validators: list[ttypes.Validator]):
        validator_updates = [
            abci.ValidatorUpdate(
                pub_key=tcrypto.PubKey(key=validator.pub_key),
                power=validator.voting_power,
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


def updateConsensusParams(params: abci.ConsensusParams, updates: abci.ConsensusParams):
    # need to mirror behaviour from tendermint/types/params.go:UpdateConsensusParams
    # but maybe modify consensusParams in-place
    pass


def applyResponseInitChain(state: tstate.State, response: abci.ResponseInitChain):
    if len(response.app_hash) > 0:
        state.app_hash = response.app_hash

    if response.consensus_params != None:
        updateConsensusParams(state.consensus_params, response.consensus_params)
