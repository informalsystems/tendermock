import asyncio
import proto.tendermint.rpc.grpc as tgrpc
from grpclib.server import Server
from grpclib import GRPCError, const
from abci_client import *

import typer

APP_HOST = "0.0.0.0"
APP_PORT = "26658"

TM_HOST = "0.0.0.0"
TM_PORT = "50051"

app = typer.Typer(pretty_exceptions_show_locals=False)


class BroadcastApiService(tgrpc.BroadcastApiBase):
    def __init__(self, abci_client):
        pass

    async def ping(self) -> "tgrpc.ResponsePing":
        raise GRPCError(const.Status.UNIMPLEMENTED)

    async def broadcast_tx(self, tx: bytes) -> "tgrpc.ResponseBroadcastTx":
        raise GRPCError(const.Status.UNIMPLEMENTED)


async def run(
    genesis_file: str,
    tendermock_host=TM_HOST,
    tendermock_port=TM_PORT,
    app_host=APP_HOST,
    app_port=APP_PORT,
):
    logging.basicConfig(filename="tendermock.log", level=logging.INFO)

    abci_client = ABCI_Client(app_host, int(app_port), genesis_file)

    server = Server([BroadcastApiService(abci_client)])
    await server.start(tendermock_host, int(tendermock_port))
    await server.wait_closed()


@app.command()
def serveBroadcastApi(
    genesis_file: str,
    tendermock_host=TM_HOST,
    tendermock_port=TM_PORT,
    app_host=APP_HOST,
    app_port=APP_PORT,
):
    response = asyncio.get_event_loop().run_until_complete(
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
