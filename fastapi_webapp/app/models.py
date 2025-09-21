from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

# User Models
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

# Project Models
class ProjectStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    MILESTONE_REACHED = "milestone_reached"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProjectMilestone(BaseModel):
    title: str
    description: str
    target_amount: float
    carbon_offset_tons: float
    deadline: datetime
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    verification_data: Optional[Dict[str, Any]] = None

class ProjectBase(BaseModel):
    title: str
    description: str
    total_funding_needed: float
    carbon_offset_goal: float  # in tons
    project_owner_id: str
    location: Optional[str] = None
    project_type: str  # solar, reforestation, etc.
    milestones: List[ProjectMilestone] = []
    status: ProjectStatus = ProjectStatus.PENDING
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class ProjectCreate(BaseModel):
    title: str
    description: str
    total_funding_needed: float
    carbon_offset_goal: float
    location: Optional[str] = None
    project_type: str
    milestones: List[ProjectMilestone] = []

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class ProjectInDB(ProjectBase):
    id: Optional[str] = Field(default=None, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class Project(ProjectInDB):
    pass

# Transaction Models
class TransactionType(str, Enum):
    CREDIT_PURCHASE = "credit_purchase"
    PROJECT_FUNDING = "project_funding"
    MILESTONE_PAYMENT = "milestone_payment"
    REFUND = "refund"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class TransactionBase(BaseModel):
    user_id: str
    project_id: Optional[str] = None
    transaction_type: TransactionType
    amount: float  # in USD
    crypto_amount: Optional[float] = None  # in ETH/MATIC
    crypto_currency: Optional[str] = None
    transaction_hash: Optional[str] = None  # blockchain transaction hash
    stripe_payment_intent_id: Optional[str] = None
    carbon_credits_purchased: Optional[float] = None  # in tons
    status: TransactionStatus = TransactionStatus.PENDING
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class TransactionCreate(BaseModel):
    user_id: str
    project_id: Optional[str] = None
    transaction_type: TransactionType
    amount: float
    carbon_credits_purchased: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class TransactionUpdate(BaseModel):
    status: Optional[TransactionStatus] = None
    transaction_hash: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    crypto_amount: Optional[float] = None
    crypto_currency: Optional[str] = None
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class TransactionInDB(TransactionBase):
    id: Optional[str] = Field(default=None, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class Transaction(TransactionInDB):
    pass

# NFT Certificate Models
class CarbonCertificateBase(BaseModel):
    project_id: str
    transaction_id: str
    user_id: str
    carbon_tons: float
    nft_token_id: Optional[str] = None
    blockchain_address: Optional[str] = None
    metadata_uri: Optional[str] = None
    verification_data: Dict[str, Any]
    issued_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class CarbonCertificateCreate(BaseModel):
    project_id: str
    transaction_id: str
    user_id: str
    carbon_tons: float
    verification_data: Dict[str, Any]

class CarbonCertificateInDB(CarbonCertificateBase):
    id: Optional[str] = Field(default=None, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class CarbonCertificate(CarbonCertificateInDB):
    pass