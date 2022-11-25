# custom image supporting x64 and aarch64 both
# until this PR merges on main https://github.com/cosmos/cosmos-sdk/pull/13993

FROM ghcr.io/rnbguy/cosmos-sdk:latest

RUN simd init node --chain-id tendermock

# genesis-validator: cosmos1true75k5hh0s94hxa7s8w29ys65s4u9n8g5fh5
RUN echo "neither fatigue grass yellow wash magic purity test achieve bridge february lecture pipe cover notable kitchen success bulk ten stable leave cushion joke square" | simd keys add node1 --recover --keyring-backend test

# genesis-validator: cosmos1mpvq0pfagrk6ed9gstdqf04n8q8d7zca3tjanj
RUN echo "height artist hobby lake tooth awful inherit local nuclear this milk area staff mountain naive vehicle forward mango lyrics retire online flock ceiling ignore" | simd keys add node2 --recover --keyring-backend test

# genesis-account: cosmos1l3dt6qtj2cj8yvw0jdtrn7depz02zzkhnwqafa
RUN echo "secret arctic earn topic brick depth vehicle digital yard hair gravity father rotate athlete table limb blade lake arch black mirror husband comic test" | simd keys add acc1 --recover --keyring-backend test

# add balance to accounts
RUN simd add-genesis-account $(simd keys show -a node1 --keyring-backend test) 5000000000stake
RUN simd add-genesis-account $(simd keys show -a node2 --keyring-backend test) 5000000000stake
RUN simd add-genesis-account $(simd keys show -a acc1 --keyring-backend test) 5000000000stake

RUN simd gentx node1 5000000000stake --chain-id=tendermock --keyring-backend test
RUN simd collect-gentxs

RUN apk add --no-cache jq
RUN cat /root/.simapp/config/genesis.json | jq '.consensus_params.evidence.max_age_duration = "172800s"' > genesis.json

RUN cat genesis.json > /root/.simapp/config/genesis.json
