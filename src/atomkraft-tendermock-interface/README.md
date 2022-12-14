This folder outlines a proposal for the interface between Tendermock and Atomkraft.
Anything should be viewed as merely a suggestion that can and very likely will be adjusted as we move along.

### Context
Tendermock helps test applications built on top of ABCI.

It bridges the gap between Atomkraft and an application.
Typically, one would
* run a small network of Tendermint nodes running the application on top
* run Atomkraft to generate a transaction trace
* feed that transaction trace to Tendermint as user-level transactions
* wait for Tendermint to come to consensus and execute the transactions

There are three main disadvantages to this approach:
* Running Tendermint takes time: Tendermint may take time to come to consensus, so executing transactions can be slow, when in reality it's not necessary to run the actual consensus engine if we just test application logic
* Control: Some things are controlled by Tendermint, which we cannot control precisely, e.g.:
    * Who proposes/votes on a proposal. (What if we want to test an edge case where it's crucial that a validator signs exactly each second block?)
    * Transaction timestamps. What if we want to test the behaviour when the time of the next block is suddenly 10 years in the future? If we run the actual Tendermint, this would mean we need to somehow manipulate the timestamp
    Tendermint gets from the system, since the time is determined by the consensus engine
    * Number of rounds to consensus. Testing app behaviour if consensus took 200 rounds to be achieved would usually mean we need to make sure that Tendermint actually goes through 200 rounds until consensus, which may take a while.
* Large networks: It's infeasible to test the app with 5,000 validators - it's just too big of a network

With Tendermock, it looks like this:
* run one instance of the application (as a server)
* run one instance of Tendermock (functions as a client)
* run Atomkraft to generate traces
* feed the traces to Tendermock - which, to the application, behaves just like Tendermint, but doesn't actually run consensus inside - it rather passes the given transactions along as given by Atomkraft
  
This means Tendermock allows...
* ...running tests faster - no need to wait for Tendermint to come to consensus
* ...precisely controlling things usually determined by Tendermint - which nodes vote/propose, how many rounds pass until consensus, the timestamps of each block, etc.
* ...simulating large networks - to the application, Tendermock can make it look like there are thousands of validators in the network, without needing to run more than a single instance.

## Tendermocks interface to the outside

To facilitate this type of carefully manipulated, fast testing,
Tendermock needs to take some input data.
Notably, transitions need to be supplied to Tendermock, and there should be a way to specify the signers and timestamps for each block.

Goals in designing this interface:
* All but the very minimal information should be optional. Setting up a simple
testcase where some transactions are given to the application
should not require putting any additional information other than
the initial state (i.e. genesis file) and the transactions (i.e. the trace).
* More fine-grained control should be possible to achieve,
but this will necessarily be harder.

There are two ways to influence Tendermocks behaviour:
* By the content of the `genesis.json` file. This file will essentially set the application
and chain status at the start of the test, see https://hub.cosmos.network/main/resources/genesis.html. The genesis file is application specific, so it will need
to be provided to Tendermock by the user.
* By the content of the transaction trace. Tendermock reads a trace that contains signed user-level transactions annotated with some optional metainformation (how many rounds until consensus, which validators signed, etc), and feeds them to the application.

### `genesis.json`

The file is defined by Tendermint and the CosmosSDK.
Eventually, it would be interesting to generate the parts of the genesis file automatically as far as possible, to ease the burden on application devs.

### Trace format

The format for traces is defined in https://github.com/informalsystems/tendermock/blob/main/atomkraft-tendermock-interface/proto/tendermock/traces.proto.
