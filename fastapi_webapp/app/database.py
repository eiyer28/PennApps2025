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

async def save_order_to_history(order_data: dict):
    """Save completed order to order history collection"""
    try:
        database = await get_database()
        orders_collection = database.order_history
        
        # Insert the order record
        result = await orders_collection.insert_one(order_data)
        print(f"Order saved to history with ID: {result.inserted_id}")
        return str(result.inserted_id)
        
    except Exception as e:
        print(f"Error saving order to history: {e}")
        # Don't fail the order if we can't save to history
        return None

async def get_user_orders(user_id: str):
    """Get all orders for a specific user"""
    try:
        database = await get_database()
        orders_collection = database.order_history
        
        # Find all orders for this user, sorted by creation date (newest first)
        cursor = orders_collection.find({"user_id": user_id}).sort("created_at", -1)
        orders = await cursor.to_list(length=None)
        
        return orders
        
    except Exception as e:
        print(f"Error fetching user orders: {e}")
        return []

async def get_user_by_id(user_id: str):
    """Get user details by user ID"""
    try:
        database = await get_database()
        users_collection = database.users
        
        # Find user by ID or email (since userId could be either)
        user = await users_collection.find_one({
            "$or": [
                {"_id": user_id},
                {"email": user_id}
            ]
        })
        if user is None:
            print(f"Could not find user: {user_id}")
            return None

        return user

    except Exception as e:
        print(f"Error fetching user by ID: {e}")
        return None

async def get_user_by_crypto_address(crypto_address: str):
    """Get user details by crypto/wallet address"""
    try:
        database = await get_database()
        users_collection = database.users

        # Find user by wallet address
        user = await users_collection.find_one({
            "address": crypto_address
        })

        if user:
            return {
                "first_name": user.get("first_name", ""),
                "last_name": user.get("last_name", ""),
                "email": user.get("email", ""),
                "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            }

        return None

    except Exception as e:
        print(f"Error fetching user by crypto address: {e}")
        return None
