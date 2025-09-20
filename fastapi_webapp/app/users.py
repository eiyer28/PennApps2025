from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from .database import get_database
from .models import User, UserCreate, UserUpdate, UserInDB
from .auth import get_current_user
from .wallet import generate_wallet
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/users/register", response_model=User)
async def register_user(
    user_data: UserCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db = Depends(get_database)
):
    """Register a new user after Auth0 authentication"""

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
        "name": user_data.name,
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

@router.get("/users/me", response_model=User)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get current user's profile"""

    auth0_id = current_user.get("sub")
    users_collection = db.get_collection("users")
    user = await users_collection.find_one({"auth0_id": auth0_id})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_response = User(**user)
    user_response.wallet_private_key = None  # Don't return private key

    return user_response

@router.put("/users/me", response_model=User)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update current user's profile"""

    auth0_id = current_user.get("sub")

    # Prepare update data
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    # Update user in database
    users_collection = db.get_collection("users")
    result = await users_collection.update_one(
        {"auth0_id": auth0_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # Get updated user
    updated_user = await users_collection.find_one({"auth0_id": auth0_id})
    user_response = User(**updated_user)
    user_response.wallet_private_key = None  # Don't return private key

    return user_response

@router.get("/users/wallet")
async def get_user_wallet(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user's wallet address (public info only)"""

    auth0_id = current_user.get("sub")
    users_collection = db.get_collection("users")
    user = await users_collection.find_one({"auth0_id": auth0_id})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "wallet_address": user.get("wallet_address"),
        "user_id": str(user["_id"])
    }