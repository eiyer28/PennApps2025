import bcrypt
from typing import Optional
from datetime import datetime
from bson import ObjectId
from .database import get_database
from .models import UserSignup, UserLogin, UserResponse, UserInDB

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
        raise ValueError("User with this email already exists")
    
    # Hash the password
    password_hash = hash_password(user_data.password)
    
    # Create user document
    user_doc = {
        "email": user_data.email,
        "password_hash": password_hash,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "created_at": datetime.utcnow()
    }
    
    # Insert user into database
    result = await database.users.insert_one(user_doc)
    
    # Return user response (without password hash)
    return UserResponse(
        _id=str(result.inserted_id),
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        created_at=user_doc["created_at"]
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
        created_at=user_doc["created_at"]
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