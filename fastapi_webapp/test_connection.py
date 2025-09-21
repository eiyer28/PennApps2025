import os
from dotenv import load_dotenv
import pymongo

load_dotenv()

mongodb_url = os.getenv("MONGODB_URL")
print(f"Testing connection to: {mongodb_url[:50]}...")

try:
    # Use synchronous pymongo for simple test
    client = pymongo.MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)

    # Test connection
    client.admin.command('ping')
    print("SUCCESS: Connected to MongoDB Atlas!")

    # List databases
    dbs = client.list_database_names()
    print(f"Available databases: {dbs}")

    client.close()

except Exception as e:
    print(f"FAILED: {e}")
    print("\nTroubleshooting steps:")
    print("1. Check Network Access in Atlas dashboard")
    print("2. Make sure your IP address is whitelisted")
    print("3. Verify credentials in connection string")