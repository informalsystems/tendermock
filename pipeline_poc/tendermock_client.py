import connector
import json

DOCKER_PATH = "docker exec -i simapp".split(" ")
SIMD_BINARY = DOCKER_PATH + ["simd"]

TENDERMOCK_HOST = "host.docker.internal"
TENDERMOCK_PORT = "26657"


class Balance:
    def __init__(self, amount, cointype):
        self.amount = amount
        self.cointype = cointype


class Account:
    def __init__(self, coin_balances, address, name, passphrase):
        self.balances = coin_balances
        self.address = address
        self.name = name
        self.passphrase = passphrase


if __name__ == "__main__":

    logfile = open("tendermint_client.log", "w+")

    # could instead e.g. read most of this from genesis
    accounts = [
        Account(
            [Balance(5000000000, "stake")],
            # neither fatigue grass yellow wash magic purity test achieve bridge february lecture pipe cover notable kitchen success bulk ten stable leave cushion joke square
            "cosmos1true75k5hh0s94hxa7s8w29ys65s4u9n8g5fh5",
            "node1",
            "tendermint",
        ),
        Account(
            [Balance(5000000000, "stake")],
            # height artist hobby lake tooth awful inherit local nuclear this milk area staff mountain naive vehicle forward mango lyrics retire online flock ceiling ignore
            "cosmos1mpvq0pfagrk6ed9gstdqf04n8q8d7zca3tjanj",
            "node2",
            "tendermint",
        ),
    ]

    # do a transfer

    sender = accounts[1]
    receiver = accounts[0]
    amount = Balance(5000, "stake")

    # query balance before transaction
    cmd = connector.CosmosCmd(
        logfile,
        SIMD_BINARY,
        f"query bank balances {sender.address} --node=http://{TENDERMOCK_HOST}:{TENDERMOCK_PORT} --output=json".split(
            " "
        ),
        [],
    )
    result = cmd.call()
    print(f"Balance before: {result}")


    # //////////////////////////////////////////////////////////////////////////////////
    # // generate & sign transaction //
    cmd = connector.CosmosCmd(
        logfile,
        SIMD_BINARY,
        f"query account {sender.address} --node=http://{TENDERMOCK_HOST}:{TENDERMOCK_PORT} --output=json".split(
            " "
        ),
        [],
    )
    result = json.loads(cmd.call())

    account_number = result["account_number"]
    sequence = result["sequence"]

    cmd = connector.CosmosCmd(
        logfile,
        SIMD_BINARY,
        f"tx bank send {sender.address} {receiver.address} {amount.amount}{amount.cointype} --from={sender.name} --chain-id=tendermock --generate-only --keyring-backend=test".split(
            " "
        ),
        [],
    )

    tx = cmd.call()

    cmd = connector.CosmosCmd(
        logfile,
        DOCKER_PATH,
        ["tee", "tx_tmp.json"],
        [tx],
    )
    cmd.call()

    cmd = connector.CosmosCmd(
        logfile,
        SIMD_BINARY,
        f"tx sign tx_tmp.json --chain-id=tendermock --from={sender.name} --offline --account-number {account_number} --sequence {sequence} --keyring-backend=test".split(
            " "
        ),
        [sender.passphrase],
    )

    signed_tx = cmd.call()

    cmd = connector.CosmosCmd(
        logfile,
        DOCKER_PATH,
        ["tee", "signed_tx_tmp.json"],
        [signed_tx],
    )
    cmd.call()

    # //////////////////////////////////////////////////////////////////////////////////
    # // broadcast tx //

    cmd = connector.CosmosCmd(
        logfile,
        SIMD_BINARY,
        f"tx broadcast --node http://{TENDERMOCK_HOST}:{TENDERMOCK_PORT} signed_tx_tmp.json".split(
            " "
        ),
        [sender.passphrase],
    )
    result = cmd.call()

    # query balance after transaction
    cmd = connector.CosmosCmd(
        logfile,
        SIMD_BINARY,
        f"query bank balances {sender.address} --node=http://{TENDERMOCK_HOST}:{TENDERMOCK_PORT} --output=json".split(
            " "
        ),
        [],
    )
    result = cmd.call()
    print(f"Balance after: {result}")
