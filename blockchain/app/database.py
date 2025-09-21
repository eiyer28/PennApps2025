import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None
    is_fallback = False

db = Database()

def format_email_extension_to_lowercase(email_address):
    """
    Converts the domain extension of an email address to lowercase.

    Args:
        email_address (str): The email address to format.

    Returns:
        str: The email address with the extension in lowercase.
    """
    if "@" not in email_address:
        return email_address  # Not a valid email format, return as is

    local_part, domain = email_address.split("@", 1)

    formatted_domain = domain.lower()

    return f"{local_part}@{formatted_domain}"

async def get_database():
    return db.database

async def connect_to_mongo():
    """Create database connection - tries MongoDB Atlas first, falls back to in-memory"""
    # Use MONGODB_CONNECTION_STRING for Atlas connection
    mongodb_url = os.getenv("MONGODB_CONNECTION_STRING")

    # Try MongoDB Atlas first
    if mongodb_url:
        try:
            print("Attempting to connect to MongoDB Atlas...")
            db.client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=5000)
            db.database = db.client.carbonchain

            # Test the connection
            await db.client.admin.command('ping')
            print("SUCCESS: Connected to MongoDB Atlas successfully!")
            db.is_fallback = False
            return

        except Exception as e:
            print(f"FAILED: MongoDB Atlas connection failed: {e}")
            print("INFO: Falling back to in-memory database for development...")

    # Fallback to in-memory database

    # Test fallback connection
    await db.client.admin.command('ping')
    print("SUCCESS: Using in-memory fallback database for development")
    print("WARNING: Data will not persist between restarts")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        if db.is_fallback:
            print("Disconnected from fallback database")
        else:
            print("Disconnected from MongoDB Atlas")

async def get_address_by_id(user_id: str):
    """Get user details by user ID"""
    try:
        database = await get_database()
        users_collection = database.users

        user_id = format_email_extension_to_lowercase(user_id)

        # Find user by ID or email (since userId could be either)
        user = await users_collection.find_one({
            "$or": [
                {"_id": user_id},
                {"email": user_id}
            ]
        })
        if not user:
            print(f"Could not find user: {user_id}")
            return None
        
        return user.get('address')
    except Exception as e:
        print(f"Error fetching user by ID: {e}")
        return None

async def get_pk_by_id(user_id: str):
    """Get user details by user ID"""
    try:
        database = await get_database()
        users_collection = database.users

        user_id = format_email_extension_to_lowercase(user_id)

        # Find user by ID or email (since userId could be either)
        user = await users_collection.find_one({
            "$or": [
                {"_id": user_id},
                {"email": user_id}
            ]
        })

        if not user:
            print(f"Could not find user: {user_id}")

        return user.get('private_key')
    except Exception as e:
        print(f"Error fetching user by ID: {e}")
        return None