#!/usr/bin/env python3
"""
Simple test script to verify the account creation system setup
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.wallet import generate_wallet
from app.database import connect_to_mongo, close_mongo_connection, get_database

async def test_wallet_generation():
    """Test wallet generation"""
    print("Testing wallet generation...")
    wallet = generate_wallet()
    print(f"Generated wallet address: {wallet['address']}")
    print(f"Private key generated: {wallet['private_key'][:10]}...")
    return True

async def test_database_connection():
    """Test MongoDB connection"""
    print("\nTesting database connection...")
    try:
        await connect_to_mongo()
        database = await get_database()

        # Get the test collection
        test_collection = database.get_collection("test_collection")

        # Test a simple operation
        result = await test_collection.insert_one({"test": "data"})
        print(f"Database connection successful, test doc ID: {result.inserted_id}")

        # Clean up test document
        await test_collection.delete_one({"_id": result.inserted_id})

        await close_mongo_connection()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("=== CarbonChain Account System Setup Test ===\n")

    # Test wallet generation
    wallet_ok = await test_wallet_generation()

    # Test database connection
    db_ok = await test_database_connection()

    print(f"\n=== Test Results ===")
    print(f"Wallet Generation: {'PASS' if wallet_ok else 'FAIL'}")
    print(f"Database Connection: {'PASS' if db_ok else 'FAIL'}")

    if wallet_ok and db_ok:
        print("\nAll systems ready for account creation!")
    else:
        print("\nSome components need configuration")

if __name__ == "__main__":
    asyncio.run(main())