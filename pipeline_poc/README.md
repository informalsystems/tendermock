## Starting up

The following subsections should each be done in a separate shell.

### ABCI App

Start the ABCI app by running, in a terminal:

```docker run --add-host=host.docker.internal:host-gateway --name tendermock -ti -p 26658:26658 -p 26656:26656 -p 9091:9091 -p 1317:1317 -p 9090:9090 imgs/testnet simd start --transport=grpc --with-tendermint=false --grpc-only --rpc.laddr=tcp://host.docker.internal:99999```

(You may need to stop and remove an existing container with the name "tendermock", if it already exists.)

You should get output like this:

```
9:55AM INF starting ABCI without Tendermint
9:55AM INF service start impl=ABCIServer module=abci-server msg={}
9:55AM INF Listening addr=0.0.0.0:26658 module=abci-server proto=tcp
```

### Tendermock

Start tendermock by running 

```python ../src/tendermock.py genesis.json --tendermock-host localhost --tendermock-port 26657 --app-host localhost --app-port 26658```

This should give some output in the ABCI window that ends with:

```
9:57AM INF commit synced commit=436F6D6D697449447B5B363420333220313434203530203230332032333120323437203131362032323020323436203237203138332031373620313532203234312039203835203135362031333420373520383220353320313420393120393220313739203133332035302033322039352036372037345D3A317D
```

### Client

Now, you can run the client that simulates a trace execution:

```python tendermock_client.py```

Right now, it executes a single transaction.