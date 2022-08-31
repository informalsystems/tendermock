import json
import grpc
import tendermint.abci.types_pb2 as atypes
import tendermint.crypto.keys_pb2 as crypto
import tendermint.abci.types_pb2_grpc as abci
import tendermint.types.params_pb2 as params
import google.protobuf.timestamp_pb2 as times
import google.protobuf.duration_pb2 as duration

address = "0.0.0.0"
port = "23456"
genesis_filename = "genesis.json"

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

def getAppstateBytesFromGenesis(filename):
    with open(filename) as genesis_file:
        genesis_json = json.load(genesis_file)
        app_state = genesis_json["app_state"]
        app_state_str = json.dumps(app_state)
        app_state_bytes = str.encode(app_state_str)
        return app_state_bytes


def buildConsensusParams():
    block_params = params.BlockParams(max_bytes=22020096, max_gas=-1)

    max_age_duration = duration.Duration()
    max_age_duration.FromSeconds(200000000)
    evidence_params = params.EvidenceParams(
        max_age_num_blocks=100000,
        max_age_duration=max_age_duration,
        max_bytes=1048576
    )

    validator_params = params.ValidatorParams(
        pub_key_types=["ed25519", "secp256k1"]
    )

    version_params = params.VersionParams(
        app=1
    )

    consensus_params = params.ConsensusParams(
        block=block_params,
        evidence=evidence_params,
        validator=validator_params,
        version=version_params
    )

    return consensus_params


def buildValidatorList():
    validators = [
        atypes.ValidatorUpdate(
            pub_key=crypto.PublicKey(
                ed25519=str.encode(node.pubkey)),
            power=node.balance)
        for node in nodes
    ]
    return validators


if __name__ == '__main__':
    with grpc.insecure_channel(f"{address}:{port}") as channel:
        stub = abci.ABCIApplicationStub(channel)
        # request.time = datetime.now().time()
        chain_id = "tendermock"

        validators = buildValidatorList()

        app_state_bytes = getAppstateBytesFromGenesis(genesis_filename)

        consensus_params = buildConsensusParams()

        timestamp = times.Timestamp()
        timestamp.GetCurrentTime()

        request = atypes.RequestInitChain(
            time=timestamp,
            chain_id=chain_id,
            consensus_params=consensus_params,
            app_state_bytes=app_state_bytes,
            initial_height=1,
            validators=validators)

        print(request)

        response = stub.InitChain(request)
