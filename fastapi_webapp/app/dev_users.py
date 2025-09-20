"""
Development user endpoints that bypass Auth0 authentication
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from .database import get_database
from .models import User, UserCreate, UserUpdate, UserInDB
from .dev_auth import is_dev_mode, get_dev_user
from .wallet import generate_wallet
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/dev/users/register", response_model=User)
async def dev_register_user(
    user_data: UserCreate,
    db = Depends(get_database)
):
    """Register a new user in development mode (no Auth0 required)"""

    if not is_dev_mode():
        raise HTTPException(status_code=403, detail="Development endpoints disabled")

    # In dev mode, use the provided auth0_id or generate one
    if not user_data.auth0_id:
        user_data.auth0_id = f"dev_{user_data.email.replace('@', '_').replace('.', '_')}"

    # Check if user already exists
    users_collection = db.get_collection("users")
    existing_user = await users_collection.find_one({"auth0_id": user_data.auth0_id})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Generate crypto wallet
    wallet = generate_wallet()

    # Create user document
    user_doc = {
        "email": user_data.email,
        "auth0_id": user_data.auth0_id,
        "name": user_data.name or "Development User",
        "wallet_address": wallet["address"],
        "wallet_private_key": wallet["private_key"],  # In production, encrypt this!
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert user into database
    result = await users_collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    # Return user data (excluding private key)
    user_response = User(**user_doc)
    user_response.wallet_private_key = None  # Don't return private key

    return user_response

@router.get("/dev/users/me", response_model=User)
async def dev_get_current_user(
    db = Depends(get_database)
):
    """Get development user profile"""

    if not is_dev_mode():
        raise HTTPException(status_code=403, detail="Development endpoints disabled")

    # Use the dev user
    dev_user = get_dev_user()
    auth0_id = dev_user["sub"]

    users_collection = db.get_collection("users")
    user = await users_collection.find_one({"auth0_id": auth0_id})

    if not user:
        raise HTTPException(status_code=404, detail="User not found. Register first using /api/v1/dev/users/register")

    user_response = User(**user)
    user_response.wallet_private_key = None  # Don't return private key

    return user_response

@router.get("/dev/users/wallet")
async def dev_get_user_wallet(
    db = Depends(get_database)
):
    """Get development user's wallet address"""

    if not is_dev_mode():
        raise HTTPException(status_code=403, detail="Development endpoints disabled")

    # Use the dev user
    dev_user = get_dev_user()
    auth0_id = dev_user["sub"]

    users_collection = db.get_collection("users")
    user = await users_collection.find_one({"auth0_id": auth0_id})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "wallet_address": user.get("wallet_address"),
        "user_id": str(user.get("_id", "unknown")),
        "dev_mode": True
    }

@router.get("/dev/status")
async def dev_status():
    """Check if development mode is enabled"""
    return {
        "dev_mode": is_dev_mode(),
        "message": "Development endpoints available" if is_dev_mode() else "Development mode disabled"
    }