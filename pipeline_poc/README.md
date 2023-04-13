## Starting up

To prepare, you need to grab a docker image:
```docker pull informalofftermatt/testnet:tendermock```


The following subsections should each be done in a separate shell.


### ABCI App

Start the ABCI app by running, in a terminal:

```docker run --add-host=host.docker.internal:host-gateway --name simapp -ti -p 26658:26658 informalofftermatt/testnet:tendermock simd start --transport=grpc --with-tendermint=false --grpc-only --rpc.laddr=tcp://host.docker.internal:99999```

(You may need to stop and remove an existing container with the name "simapp", if it already exists.
You can prefix the above command with `docker stop simapp; docker rm simapp;` if that's needed)

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
Output should look like this:
```
Balance before: {"balances":[{"denom":"stake","amount":"4999995000"}],"pagination":{"next_key":null,"total":"0"}}

Balance after: {"balances":[{"denom":"stake","amount":"4999990000"}],"pagination":{"next_key":null,"total":"0"}}
```

You can run the client multiple times, and each time should decrease the token amount by 5000.


https://user-images.githubusercontent.com/57488781/201970697-6f3c9039-d0fb-4437-a862-9d4d4398ea31.mp4



## Multi Chain Test

Start chains by running, in separate terminals:

```
docker stop simapp; docker rm simapp; docker run --add-host=host.docker.internal:host-gateway --name simapp -p 26658:26658 -ti informalofftermatt/testnet:tendermock simd start --transport=grpc --with-tendermint=false --grpc-only --rpc.laddr=tcp://host.docker.internal:99999
```

```
docker stop simapp2; docker rm simapp2; docker run --add-host=host.docker.internal:host-gateway --name simapp2 -p 36658:26658 -ti informalofftermatt/testnet:tendermock simd start --transport=grpc --with-tendermint=false --grpc-only --rpc.laddr=tcp://host.docker.internal:99999
```

```
python3 ../src/tendermock.py genesis.json --tendermock-host localhost --tendermock-port 26657 --app-addresses localhost:36658,localhost:26658
```

Lastly, run

```python3 tendermock_multichainclient.py```

Expected output is 
```
Balance before on Simapp1: {"balances":[{"denom":"stake","amount":"5000000000"}],"pagination":{"next_key":null,"total":"0"}}

Balance before on Simapp2: {"balances":[{"denom":"stake","amount":"5000000000"}],"pagination":{"next_key":null,"total":"0"}}

Balance after on Simapp1: {"balances":[{"denom":"stake","amount":"4999995000"}],"pagination":{"next_key":null,"total":"0"}}

Balance after on Simapp2: {"balances":[{"denom":"stake","amount":"4999995000"}],"pagination":{"next_key":null,"total":"0"}}
```