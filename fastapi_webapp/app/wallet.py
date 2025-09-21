from web3 import Web3
from eth_account import Account
import secrets

def generate_wallet():
    """Generate a new Ethereum wallet with private key and address"""
    # Generate private key
    private_key = "0x" + secrets.token_hex(32)

    # Create account from private key
    account = Account.from_key(private_key)

    return {
        "address": account.address,
        "private_key": private_key
    }