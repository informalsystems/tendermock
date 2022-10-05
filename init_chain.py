import json
import grpc
import proto.tendermint.abci as abci
import proto.cosmos.crypto.ed25519 as crypto
import proto.tendermint.types as ttypes




class RequestInitChainFactory:
    def createAppstateBytes(self, genesis_json):
        app_state = genesis_json["app_state"]
        app_state_str = json.dumps(app_state)
        app_state_bytes = str.encode(app_state_str)
        return app_state_bytes

    def createConsensusParams(self, genesis_json):
        genesis_params = genesis_json["consensus_params"]
    

        consensus_params = abci.ConsensusParams().from_dict(genesis_params)

        return consensus_params

    def createValidatorList(self, validators: list[ttypes.Validator]):
        validator_updates = [
            abci.ValidatorUpdate(
                pub_key=crypto.PubKey(key=validator.pub_key),
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
