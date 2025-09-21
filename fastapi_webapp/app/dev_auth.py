"""
Development authentication bypass for testing without Auth0
"""

import os
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException
from dotenv import load_dotenv

load_dotenv()

def is_dev_mode() -> bool:
    """Check if we're in development mode"""
    return os.getenv("DEV_MODE", "false").lower() == "true"

def get_dev_user() -> Dict[str, Any]:
    """Return a mock user for development mode"""
    return {
        "sub": "dev_user_123",  # This is the Auth0 ID equivalent
        "email": "dev@carbonchain.com",
        "name": "Development User"
    }

def optional_auth_dependency() -> Optional[Dict[str, Any]]:
    """
    Return mock user in dev mode, None in production mode
    This allows endpoints to work with or without authentication
    """
    if is_dev_mode():
        return get_dev_user()
    return None