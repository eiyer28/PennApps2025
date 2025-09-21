import os
from dotenv import load_dotenv
import pymongo
import ssl
import dns.resolver

load_dotenv()

mongodb_url = os.getenv("MONGODB_CONNECTION_STRING")
print(f"Testing connection to Atlas...")

# Try different connection strategies
strategies = [
    {
        "name": "Basic connection",
        "options": {}
    },
    {
        "name": "Extended timeout",
        "options": {"serverSelectionTimeoutMS": 10000, "connectTimeoutMS": 10000}
    },
    {
        "name": "SSL explicit",
        "options": {
            "serverSelectionTimeoutMS": 10000,
            "ssl": True,
            "ssl_cert_reqs": ssl.CERT_NONE
        }
    }
]

for strategy in strategies:
    print(f"\nTrying: {strategy['name']}")
    try:
        client = pymongo.MongoClient(mongodb_url, **strategy['options'])

        # Test connection
        result = client.admin.command('ping')
        print(f"SUCCESS: {result}")

        # List databases
        dbs = client.list_database_names()
        print(f"Available databases: {dbs}")

        client.close()
        break

    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")
        continue

print("\nIf all strategies failed, possible issues:")
print("1. Corporate firewall blocking MongoDB Atlas")
print("2. DNS resolution issues")
print("3. Network configuration problems")
print("4. MongoDB Atlas cluster not fully initialized")

# Test basic internet connectivity
print("\nTesting basic connectivity...")
try:
    import requests
    response = requests.get("https://www.google.com", timeout=5)
    print(f"Internet connection: OK (status {response.status_code})")
except Exception as e:
    print(f"Internet connection: FAILED ({e})")