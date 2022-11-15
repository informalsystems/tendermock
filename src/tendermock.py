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
from jsonrpcserver import method, serve, Success, dispatch, Result
from http.server import BaseHTTPRequestHandler, HTTPServer
from hexbytes import HexBytes
import base64

import typer

APP_HOST = "0.0.0.0"
APP_PORT = "26658"

TM_HOST = "0.0.0.0"
TM_PORT = "26657"

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


class TendermintRPC:
    def __init__(self, abci_client: ABCI_Client):
        self.abci_client = abci_client

    ## broadcasts
    # in Tendermock, all broadcasts block until the block with the transaction was executed

    # does not need to return any response... but just doing sync should be fine
    def broadcast_tx_async(self, tx) -> Result:  # -> ResultBroadcastTx:
        print("Hit endpoint broadcast_tx_async")
        checkTxResponse, _ = self.broadcast(tx)
        return Success({"response": checkTxResponse.to_json()})

    # waits for the response for checkTx
    def broadcast_tx_sync(self, tx) -> Result:
        print("> Hit endpoint broadcast_tx_sync")
        _, deliverTxResponse = self.broadcast(tx)
        return Success({"response": deliverTxResponse.to_json()})

    def broadcast(self, tx):
        print("broadcasting")
        print(tx)
        tx_bytes = base64.b64decode(tx)
        print(tx_bytes)

        checkTxResponse = self.abci_client.checkTx(tx_bytes)

        tx = tmock.Transaction(signed_tx=tx_bytes)
        block = tmock.Block(
            txs=[
                tx,
            ]
        )

        deliverTxResponse = self.abci_client.runBlock(block)[0]

        print("Ran block")

        return checkTxResponse, deliverTxResponse

    ## info queries
    def abci_query(self, data, path, height, prove) -> Result:
        print("Hit endpoint: ABCI Query")
        print("data: " + str(data))
        print("path: " + str(path))
        print("height: " + str(height))
        print("prove: " + str(prove))

        response = self.abci_client.abci_query(data, path, height, prove)
        return Success({"response": response.to_dict()})


async def run(
    genesis_file: str,
    tendermock_host=TM_HOST,
    tendermock_port=TM_PORT,
    app_host=APP_HOST,
    app_port=APP_PORT,
):
    test_tx = "Co4BCosBChwvY29zbW9zLmJhbmsudjFiZXRhMS5Nc2dTZW5kEmsKLWNvc21vczF4NjN5MnA3d3pzeWY5bG4wYXQ1NnZkcGUzeDY2amFmOXF6aDg2dBItY29zbW9zMTUzcnBkbnAzamNxNGtwYWM4bmpseWY0Z21mNzI0aG02cmVwdTcyGgsKBXN0YWtlEgI1MBJYClAKRgofL2Nvc21vcy5jcnlwdG8uc2VjcDI1NmsxLlB1YktleRIjCiECwGJJVnYe3/6jqqAGuOVFuR9HDewkORvt7DUZ50kJuwwSBAoCCAEYARIEEMCaDBpAsteyOMZ4NDkRGSJhBW8AU1Zvix8w7xvcviHZmDueiq9YbKcGsS/G8YsyAvIMzhQvzz/FwOVvbKq7Bc0Mejxp9g=="

    logging.basicConfig(filename="tendermock.log", level=logging.INFO)

    abci_client = ABCI_Client(app_host, int(app_port), genesis_file)

    abci_client.runBlock(block=tmock.Block(txs=[]))

    tendermintRPC = TendermintRPC(abci_client)

    tendermintRPC.broadcast_tx_sync(test_tx)
    
    # exit()

    class RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            response = dispatch(
                self.rfile.read(int(str(self.headers["Content-Length"]))).decode(),
                {
                    "broadcast_tx_sync": tendermintRPC.broadcast_tx_sync,
                    "broadcast_tx_async": tendermintRPC.broadcast_tx_async,
                    "abci_query": tendermintRPC.abci_query,
                },
            )
            if response is not None:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(str(response).encode())
            print(response)

    

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
