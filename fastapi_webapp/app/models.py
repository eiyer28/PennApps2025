from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime

# Simple authentication models
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    email: str
    first_name: str
    last_name: str
    created_at: datetime
    address: str

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

class UserInDB(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    email: str
    password_hash: str
    first_name: str
    last_name: str
    created_at: datetime
    address: str
    private_key: str

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

# Purchase-related models
class ProjectData(BaseModel):
    id: str
    name: Optional[str] = None
    price: Optional[str] = None
    registry: Optional[str] = None

class AssetSource(BaseModel):
    sourceId: str
    purchasePrice: float
    supply: float
    poolName: Optional[str] = None
    # Additional fields required for Carbonmark quote/order API
    assetPriceSourceId: Optional[str] = None
    listingId: Optional[str] = None
    pool: Optional[str] = None

class SupplierSelection(BaseModel):
    selectedSources: list[AssetSource]
    totalCost: float
    totalSupply: float
    canFulfillQuantity: bool
    costExceedsExpected: bool

class PurchaseRequest(BaseModel):
    # Retirement data
    quantity: float
    certificateFirstName: str
    certificateLastName: str
    retirementMessage: str
    projectId: str
    totalCost: float
    
    # User and project info
    userId: Optional[str] = None
    projectData: ProjectData
    
    # Supplier information (populated by backend)
    supplierSelection: Optional[SupplierSelection] = None

class PurchaseConfirmationRequest(BaseModel):
    # Quote information
    quoteId: str
    
    # Retirement certificate data
    certificateFirstName: str
    certificateLastName: str
    retirementMessage: str
    
    # User info
    userId: Optional[str] = None
    
    # Project data (for blockchain save)
    projectId: Optional[str] = None
    projectName: Optional[str] = None
    projectUrl: Optional[str] = None
    projectRegistry: Optional[str] = None

# Order execution models for Carbonmark API
class OrderItem(BaseModel):
    """Individual order item for Carbonmark API"""
    sourceId: str
    quantity: str  # Carbonmark expects string format
    price: str     # Carbonmark expects string format

class RetirementDetails(BaseModel):
    """Retirement details for Carbonmark API"""
    retiringEntityName: str
    retirementMessage: str
    consumptionCountryCode: str = "US"  # Default to US
    consumptionPeriodStart: str
    consumptionPeriodEnd: str

class CarbonmarkOrderRequest(BaseModel):
    """Request body for Carbonmark /orders endpoint"""
    quote_uuid: str  # Carbonmark quote UUID (required)
    orderItems: list[OrderItem]
    retirementDetails: RetirementDetails

class CarbonmarkOrderResponse(BaseModel):
    """Response from Carbonmark /orders endpoint"""
    orderId: str
    orderStatus: str
    items: list[Dict[str, Any]]
    createdAt: str
    updatedAt: str
    totalCarbonQuantity: str
    totalPrice: str
    retirementDetails: Optional[Dict[str, Any]] = None

class QuoteStorage(BaseModel):
    """Stored quote data for validation before order execution"""
    quoteId: str
    carbonmarkQuoteId: Optional[str] = None  # Store Carbonmark's quote UUID
    projectId: str
    quantity: float
    selectedSources: list[AssetSource]
    totalCost: float
    createdAt: datetime
    expiresAt: datetime
    status: str = "active"

class PurchaseResponse(BaseModel):
    success: bool
    message: str
    orderId: Optional[str] = None
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None
    supplierSelection: Optional[SupplierSelection] = None
    carbonmarkOrder: Optional[CarbonmarkOrderResponse] = None

class OrderHistory(BaseModel):
    """Order history record for MongoDB storage"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: Optional[str] = None
    order_id: str  # Carbonmark order ID
    quote_id: str  # Our internal quote ID
    carbonmark_quote_id: Optional[str] = None  # Carbonmark quote UUID
    project_id: str
    project_name: Optional[str] = None
    quantity: float
    total_cost: float
    certificate_name: str  # Full name for retirement certificate
    retirement_message: str
    order_status: str = "completed"
    created_at: datetime
    carbonmark_response: Optional[Dict[str, Any]] = None  # Store full Carbonmark response
    sources: Optional[List[AssetSource]] = None  # Store selected sources for blockchain
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )