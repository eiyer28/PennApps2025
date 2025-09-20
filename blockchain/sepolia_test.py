from web3 import Web3
import os
from dotenv import load_dotenv
load_dotenv("../.env")

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CHAIN_ID = int(os.getenv("CHAIN_ID"))

w3 = Web3(Web3.HTTPProvider(RPC_URL))
print(w3.is_connected())

account = w3.eth.account.from_key(PRIVATE_KEY)
# def build_tx(sender=None):
#     sender = sender or account.address
# return {
#     "from": sender,
#     "nonce": w3.eth.get_transaction_count(sender),
#     "chainId": CHAIN_ID,
#     # EIP-1559 gas params (fallback to legacy if needed)
#     "maxFeePerGas": w3.to_wei("1.5", "gwei"),
#     "maxPriorityFeePerGas": w3.to_wei("1", "gwei"),
#     "gas": 500_000,
# }
#
# Loading your contract ABIs
#
# If you compile with Hardhat or Foundry, point to the JSON artifact’s abi field.
# import json
#
# with open("artifacts/ProjectRegistry.json") as f:
#     registry_abi = json.load(f)["abi"]
# with open("artifacts/CreditToken.json") as f:
#     credit_abi = json.load(f)["abi"]
# with open("artifacts/IERC20.json") as f:
#     erc20_abi = json.load(f)["abi"]
#
# REGISTRY = w3.eth.contract(address=Web3.to_checksum_address(os.getenv("REGISTRY_ADDR")), abi=registry_abi)
# CREDIT = w3.eth.contract(address=Web3.to_checksum_address(os.getenv("CREDIT_ADDR")), abi=credit_abi)
# USDC = w3.eth.contract(address=Web3.to_checksum_address(os.getenv("USDC_ADDR")), abi=erc20_abi)
#
# Read-only examples