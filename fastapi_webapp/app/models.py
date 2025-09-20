from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, Annotated
from datetime import datetime

class UserBase(BaseModel):
    email: str
    auth0_id: str
    name: Optional[str] = None
    wallet_address: Optional[str] = None
    wallet_private_key: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    auth0_id: str
    name: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    profile_picture: Optional[str] = None
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class UserInDB(UserBase):
    id: Optional[str] = Field(default=None, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class User(UserInDB):
    pass