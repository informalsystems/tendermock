import asyncio
from tabnanny import check
from proto.tendermint.abci import ResponseDeliverTx
import proto.tendermint.rpc.grpc as tgrpc
import proto.tendermock as tmock
from grpclib.server import Server
from grpclib import GRPCError, const
from abci_client import *
import nest_asyncio
import time
import xmlrpc.server as rpc
from jsonrpcserver import Success, method, serve
import proto.tendermint.abci as abci
import hashlib
from jsonrpcserver import method, serve, Success, dispatch
from http.server import BaseHTTPRequestHandler, HTTPServer

import typer

APP_HOST = "0.0.0.0"
APP_PORT = "26658"

TM_HOST = "0.0.0.0"
TM_PORT = "26657"

app = typer.Typer(pretty_exceptions_show_locals=False)


class ResultBroadcastTx:
    code: int = "0"
    data: bytes = b""
    log: str = ""
    codespace: str = ""

    hash: bytes = b""


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


class TendermintRPC:
    def __init__(self, abci_client: ABCI_Client):
        self.abci_client = abci_client

    ## broadcasts
    # in Tendermock, all broadcasts block until the block with the transaction was executed

    @method
    # does not need to return any response... but just doing sync should be fine
    def broadcast_tx_async(self, tx: bytes) -> ResultBroadcastTx:
        print("Hit endpoint broadcast_tx_async")
        return self.broadcast(tx)

    # waits for the response for checkTx
    def broadcast_tx_sync(self, tx: bytes) -> ResultBroadcastTx:
        print("Hit endpoint broadcast_tx_sync")
        return self.broadcast(tx)

    def broadcast(self, tx: bytes) -> ResultBroadcastTx:
        print(tx)
        tx_bytes = bytes(tx)

        checkTxResponse = self.abci_client.checkTx(tx_bytes)

        tx = tmock.Transaction(signed_tx=tx_bytes)
        block = tmock.Block(
            txs=[
                tx,
            ]
        )

        self.abci_client.runBlock(block)

        print("Ran block")

        result = ResultBroadcastTx()
        result.code = checkTxResponse.code
        result.codespace = checkTxResponse.codespace
        result.data = checkTxResponse.data
        result.log = checkTxResponse.log
        result.hash = hashlib.sha256(tx)

        return result


async def run(
    genesis_file: str,
    tendermock_host=TM_HOST,
    tendermock_port=TM_PORT,
    app_host=APP_HOST,
    app_port=APP_PORT,
):
    logging.basicConfig(filename="tendermock.log", level=logging.INFO)

    abci_client = ABCI_Client(app_host, int(app_port), genesis_file)

    abci_client.runBlock(block=tmock.Block(txs=[]))

    test_tx = b"\n\x8e\x01\n\x8b\x01\n\x1c/cosmos.bank.v1beta1.MsgSend\x12k\n-cosmos153rpdnp3jcq4kpac8njlyf4gmf724hm6repu72\x12-cosmos1x63y2p7wzsyf9ln0at56vdpe3x66jaf9qzh86t\x1a\x0b\n\x05stake\x12\x0250\x12V\nN\nF\n\x1f/cosmos.crypto.secp256k1.PubKey\x12#\n!\x02'\x11\x08]\xb0\x91z<\xd85v\xe5OR\xc5\xefM\xa6{pb#\\),\t[\x07|8\xd6\xa1\x12\x04\n\x02\x08\x01\x12\x04\x10\xc0\x9a\x0c\x1a@\xfa!'v\xa1T\xac\xd4\xe5\xe0\x19\xefL\x0f\xf0\t\xb0\x94\xbfk^m\x0f\xa72\x84\xb1\xdaeY\x95\xbd_\x16c\xdf3NZ\x0f\xf6v\xad\xc8\xa8\xbbFE\xe8Y\x06\x9f\xa7\xf9\x14\x8f\x8e]\xaf\x01\xb3\x1dH\x92"

    # service = BroadcastApiService(abci_client)

    # server = Server()
    # await server.start(tendermock_host, int(tendermock_port))

    tendermintRPC = TendermintRPC(abci_client)

    class RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            response = dispatch(
                self.rfile.read(int(str(self.headers["Content-Length"]))).decode(),
                {
                    "broadcast_tx_sync": tendermintRPC.broadcast_tx_sync,
                    "broadcast_tx_async": tendermintRPC.broadcast_tx_async,
                },
            )
            if response is not None:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(str(response).encode())

    HTTPServer((tendermock_host, int(tendermock_port)), RequestHandler).serve_forever()


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
