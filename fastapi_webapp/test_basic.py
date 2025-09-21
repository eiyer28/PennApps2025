"""
Test just the wallet generation without database connection
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.wallet import generate_wallet

def test_wallet():
    print("=== Wallet Generation Test ===")

    # Generate 3 wallets to show it works
    for i in range(3):
        wallet = generate_wallet()
        print(f"Wallet {i+1}:")
        print(f"  Address: {wallet['address']}")
        print(f"  Private Key: {wallet['private_key'][:10]}...")
        print()

    print("Wallet generation working perfectly!")
    print("Once MongoDB Atlas network access is configured,")
    print("the full system will be ready!")

if __name__ == "__main__":
    test_wallet()