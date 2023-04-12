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
        self.abci_client.runBlock(block)


class TendermintRPC:
    def __init__(self, abci_client: ABCI_Client):
        self.abci_client = abci_client

    ## broadcasts
    # in Tendermock, all broadcasts block until the block with the transaction was executed

    # does not need to return any response... but just doing sync should be fine
    def broadcast_tx_async(self, tx) -> Result:
        print(">>>> Hit endpoint broadcast_tx_async")
        checkTxResponse, _ = self.broadcast(tx)
        return Success()

    # waits for the response for checkTx
    def broadcast_tx_sync(self, tx) -> Result:
        print(">>>> Hit endpoint broadcast_tx_sync")
        _, deliverTxResponse = self.broadcast(tx)
        return Success()

    def broadcast(self, tx):
        print("> broadcasting a transition")
        tx_bytes = base64.b64decode(tx)

        logging.info("Letting first application check the transaction")
        
        checkTxResponse = self.abci_client.checkTx(tx_bytes)

        tx = tmock.Transaction(signed_tx=tx_bytes)
        block = tmock.Block(
            txs=[
                tx,
            ]
        )

        deliverTxResponse = self.abci_client.runBlock(block)

        print("> finished broadcasting")

        return checkTxResponse, deliverTxResponse

    ## info queries
    def abci_query(self, data, path, height, prove) -> Result:
        logging.info(">>>> Hit endpoint abci_query")
        logging.info("data: " + str(data))
        logging.info("path: " + str(path))
        logging.info("height: " + str(height))
        logging.info("prove: " + str(prove))

        response = self.abci_client.abci_query(data, path, height, prove)
        return Success({"response": response.to_dict()})

    def block(self) -> Result:
        """
        TODO: This method is a placeholder that simply returns a success.
        If needed, implement properly in the future.
        """
        logging.info("Hit endpoint block")
        
        return Success({"response": True})


async def run(
    genesis_file: str,
    tendermock_host=TM_HOST,
    tendermock_port=TM_PORT,
    app_addresses: list[(str, str)]= [(APP_HOST, APP_PORT)]
):
    test_tx = "Co4BCosBChwvY29zbW9zLmJhbmsudjFiZXRhMS5Nc2dTZW5kEmsKLWNvc21vczF4NjN5MnA3d3pzeWY5bG4wYXQ1NnZkcGUzeDY2amFmOXF6aDg2dBItY29zbW9zMTUzcnBkbnAzamNxNGtwYWM4bmpseWY0Z21mNzI0aG02cmVwdTcyGgsKBXN0YWtlEgI1MBJYClAKRgofL2Nvc21vcy5jcnlwdG8uc2VjcDI1NmsxLlB1YktleRIjCiECwGJJVnYe3/6jqqAGuOVFuR9HDewkORvt7DUZ50kJuwwSBAoCCAEYARIEEMCaDBpAsteyOMZ4NDkRGSJhBW8AU1Zvix8w7xvcviHZmDueiq9YbKcGsS/G8YsyAvIMzhQvzz/FwOVvbKq7Bc0Mejxp9g=="

    logging.basicConfig(filename="tendermock.log", level=logging.INFO)


    abci_client = ABCI_Client(app_addresses, genesis_file)

    # need to run an empty block, as the app misbehaves when queried before running the first block
    abci_client.runBlock(block=tmock.Block(txs=[]))

    tendermintRPC = TendermintRPC(abci_client)

    # tendermintRPC.broadcast_tx_sync(test_tx)
    
    # exit()

    class RequestHandler(BaseHTTPRequestHandler):
        def dispatchHelper(self) -> str:
            request = self.rfile.read(int(str(self.headers["Content-Length"]))).decode()
            logging.info(f"Dispatching request: {request}")
            return request
            
        def do_POST(self) -> None:
            response = dispatch(
                self.dispatchHelper(),
                {
                    "broadcast_tx_sync": tendermintRPC.broadcast_tx_sync,
                    "broadcast_tx_async": tendermintRPC.broadcast_tx_async,
                    "abci_query": tendermintRPC.abci_query,
                    "block": tendermintRPC.block
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
    app_addresses: str = [f"{APP_HOST}:{APP_PORT}"]
):
    print(f">>>> Running tendermock with genesis file {genesis_file}")
    print(f"> Listening on {tendermock_host}:{tendermock_port}")
    # allows nesting event loops, see https://pypi.org/project/nest-asyncio/
    nest_asyncio.apply()

    app_addresses = [(address.split(":")[0], address.split(":")[1]) for address in app_addresses.split(",")]

    response = asyncio.run(
        run(
            genesis_file,
            tendermock_host=tendermock_host,
            tendermock_port=tendermock_port,
            app_addresses=app_addresses
        )
    )


if __name__ == "__main__":
    app()
