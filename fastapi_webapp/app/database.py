import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
from dotenv import load_dotenv
from .fallback_db import FallbackClient

# Load environment variables
load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None
    is_fallback = False

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """Create database connection - tries MongoDB Atlas first, falls back to in-memory"""
    mongodb_url = os.getenv("MONGODB_URL")

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
    db.client = FallbackClient()
    db.database = db.client.carbonchain
    db.is_fallback = True

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

async def create_indexes():
    """Create database indexes for optimal performance"""
    if db.database is None:
        print("Database not connected, skipping index creation")
        return

    try:
        # User collection indexes
        await db.database.users.create_index("auth0_id", unique=True)
        await db.database.users.create_index("email", unique=True)
        await db.database.users.create_index("wallet_address")

        # Project collection indexes
        await db.database.projects.create_index("project_owner_id")
        await db.database.projects.create_index("status")
        await db.database.projects.create_index("project_type")
        await db.database.projects.create_index("created_at")

        # Transaction collection indexes
        await db.database.transactions.create_index("user_id")
        await db.database.transactions.create_index("project_id")
        await db.database.transactions.create_index("transaction_type")
        await db.database.transactions.create_index("status")
        await db.database.transactions.create_index("transaction_hash")
        await db.database.transactions.create_index("stripe_payment_intent_id")
        await db.database.transactions.create_index("created_at")

        # Carbon certificate collection indexes
        await db.database.carbon_certificates.create_index("user_id")
        await db.database.carbon_certificates.create_index("project_id")
        await db.database.carbon_certificates.create_index("transaction_id")
        await db.database.carbon_certificates.create_index("nft_token_id")
        await db.database.carbon_certificates.create_index("blockchain_address")

        print("Database indexes created successfully")

    except Exception as e:
        print(f"Error creating indexes: {e}")

async def get_collection(collection_name: str):
    """Get a specific collection from the database"""
    if db.database is None:
        raise Exception("Database not connected")
    return getattr(db.database, collection_name)