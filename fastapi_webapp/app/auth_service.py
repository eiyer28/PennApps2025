import os

import bcrypt
from typing import Optional
from datetime import datetime

import web3
from bson import ObjectId
from eth_account import Account
import secrets

from web3 import Web3

from .database import get_database
from .models import UserSignup, UserLogin, UserResponse, UserInDB

INITIAL_WEI = 100000000000000000000

SUGAR_ADDRESS = os.getenv('SUGAR_ADDRESS')
SUGAR_PRIVATE_KEY = os.getenv('SUGAR_PRIVATE_KEY')
ETH_NODE_URL = os.getenv('ETH_NODE_URL')


def transfer_initial_eth(to_address):
    w3 = Web3(Web3.HTTPProvider(ETH_NODE_URL))
    from_address = SUGAR_ADDRESS

    nonce = w3.eth.get_transaction_count(from_address)
    value = INITIAL_WEI

    tx = {
        'nonce': nonce,
        'to': to_address,
        'value': value,
        'gas': 21000,
        'gasPrice': w3.eth.gas_price,
    }

    # Ensure private key starts with '0x'
    private_key = SUGAR_PRIVATE_KEY
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return tx_hash.hex()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

async def create_user(user_data: UserSignup) -> UserResponse:
    """Create a new user in the database"""
    database = await get_database()
    
    # Check if user already exists
    existing_user = await database.users.find_one({"email": user_data.email})
    if existing_user:
        raise ValueError(f"User with this email already exists {user_data.email}")
    
    # Hash the password
    password_hash = hash_password(user_data.password)

    private_key = secrets.token_hex(32)

    account = Account.from_key('0x' + private_key)
    try:
        transfer_initial_eth(account.address)
    except Exception as e:
        print(e)

    # Create user document
    user_doc = {
        "email": user_data.email,
        "password_hash": password_hash,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "created_at": datetime.utcnow(),
        "address": account.address,
        "private_key": private_key
    }
    
    # Insert user into database
    result = await database.users.insert_one(user_doc)
    
    # Return user response (without password hash)
    return UserResponse(
        _id=str(result.inserted_id),
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        created_at=user_doc["created_at"],
        address=account.address
    )

async def authenticate_user(email: str, password: str) -> Optional[UserResponse]:
    """Authenticate a user with email and password"""
    database = await get_database()
    
    # Find user by email
    user_doc = await database.users.find_one({"email": email})
    if not user_doc:
        return None
    
    # Verify password
    if not verify_password(password, user_doc["password_hash"]):
        return None
    
    # Return user response (without password hash)
    return UserResponse(
        _id=str(user_doc["_id"]),
        email=user_doc["email"],
        first_name=user_doc["first_name"],
        last_name=user_doc["last_name"],
        created_at=user_doc["created_at"],
        address=user_doc["address"]

    )

async def get_user_by_email(email: str) -> Optional[UserResponse]:
    """Get a user by email address"""
    database = await get_database()
    
    user_doc = await database.users.find_one({"email": email})
    if not user_doc:
        return None
    
    return UserResponse(
        _id=str(user_doc["_id"]),
        email=user_doc["email"],
        first_name=user_doc["first_name"],
        last_name=user_doc["last_name"],
        created_at=user_doc["created_at"]
    )
