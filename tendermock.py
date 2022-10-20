import asyncio
import proto.tendermint.rpc.grpc as tgrpc
import proto.tendermock as tmock
from grpclib.server import Server
from grpclib import GRPCError, const
from abci_client import *
import nest_asyncio
import time

import typer

APP_HOST = "0.0.0.0"
APP_PORT = "26658"

TM_HOST = "0.0.0.0"
TM_PORT = "50051"

app = typer.Typer(pretty_exceptions_show_locals=False)


class BroadcastApiService(tgrpc.BroadcastApiBase):
    def __init__(self, abci_client: ABCI_Client):
        self.abci_client = abci_client

    async def ping(self) -> "tgrpc.ResponsePing":
        raise GRPCError(const.Status.UNIMPLEMENTED)

    async def broadcast_tx(self, tx: bytes) -> "tgrpc.ResponseBroadcastTx":
        tx = tmock.Transaction(signed_tx=tx)
        block = tmock.Block(
            txs=[
                tx,
            ]
        )
        print(block)
        self.abci_client.runBlock(block)


async def run(
    genesis_file: str,
    tendermock_host=TM_HOST,
    tendermock_port=TM_PORT,
    app_host=APP_HOST,
    app_port=APP_PORT,
):
    logging.basicConfig(filename="tendermock.log", level=logging.INFO)

    abci_client = ABCI_Client(app_host, int(app_port), genesis_file)

    service = BroadcastApiService(abci_client)

    server = Server([service])
    await server.start(tendermock_host, int(tendermock_port))

    time.sleep(0.1)

    await service.broadcast_tx(
        tx="""Co4BCosBChwvY29zbW9zLmJhbmsudjFiZXRhMS5Nc2dTZW5kEmsKLWNvc21vczE1M3JwZG5wM2pjcTRrcGFjOG5qbHlmNGdtZjcyNGhtNnJlcHU3MhItY29zbW9zMXg2M3kycDd3enN5ZjlsbjBhdDU2dmRwZTN4NjZqYWY5cXpoODZ0GgsKBXN0YWtlEgI1MBJWCk4KRgofL2Nvc21vcy5jcnlwdG8uc2VjcDI1NmsxLlB1YktleRIjCiECJxEIXbCRejzYNXblT1LF702me3BiI1wpLAlbB3w41qESBAoCCAESBBDAmgwaQPohJ3ahVKzU5eAZ70wP8AmwlL9rXm0PpzKEsdplWZW9XxZj3zNOWg/2dq3IqLtGRehZBp+n+RSPjl2vAbMdSJI=""".encode(
            "ascii"
        )
    )

    await server.wait_closed()


@app.command()
def serveBroadcastApi(
    genesis_file: str,
    tendermock_host=TM_HOST,
    tendermock_port=TM_PORT,
    app_host=APP_HOST,
    app_port=APP_PORT,
):
    # allows nesting event loops, see https://pypi.org/project/nest-asyncio/
    nest_asyncio.apply()

    response = asyncio.run(
        run(
            genesis_file,
            tendermock_host=tendermock_host,
            tendermock_port=tendermock_port,
            app_host=app_host,
            app_port=app_port,
        )
    )


if __name__ == "__main__":
    app()
