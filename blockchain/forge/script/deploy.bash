#!/usr/bin/env bash
# Alternative without jq (parses text output)
set -euo pipefail

echo "Deploying CarbonProject..."

RPC_URL=http://localhost:8545
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

CARBON_PROJ="src/CarbonProject.sol:CarbonProject"
CARBON_ESCROW="src/CarbonEscrow.sol:CarbonEscrow"

ARGS=(
  0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
  0x70997970C51812dc3A010C7d01b50e0d17dc79C8
  0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC
  "1234"
  12345
)


out=$(forge create "$CARBON_PROJ" \
  --broadcast \
  --rpc-url "$RPC_URL" \
  --private-key "$PRIVATE_KEY")

DEPLOYED_TO=$(awk -F': ' '/^Deployed to:/ {print $2; exit}' <<<"$out")
if [[ -z "$DEPLOYED_TO" ]]; then
  echo "Failed to parse deployed address from forge output:"
  echo "$out"
  exit 1
fi

echo "Project Contract deployed to: $DEPLOYED_TO"

echo "Deploying CarbonEscrow..."

out=$(forge create "$CARBON_ESCROW" \
  --broadcast \
  --rpc-url "$RPC_URL" \
  --private-key "$PRIVATE_KEY" \
  --constructor-args "$DEPLOYED_TO")

DEPLOYED_TO=$(awk -F': ' '/^Deployed to:/ {print $2; exit}' <<<"$out")
if [[ -z "$DEPLOYED_TO" ]]; then
  echo "Failed to parse deployed address from forge output:"
  echo "$out"
  exit 1
fi

echo "Escrow Contract deployed to: $DEPLOYED_TO"

