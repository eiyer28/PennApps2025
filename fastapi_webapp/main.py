from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query
from fastapi.responses import JSONResponse
import requests

import uvicorn
import os
from dotenv import load_dotenv
from datetime import datetime

# Import our modules
from app.database import connect_to_mongo, close_mongo_connection, save_order_to_history, get_user_orders, get_user_by_id
from app.models import (
    UserSignup, UserLogin, UserResponse, PurchaseRequest, PurchaseConfirmationRequest, 
    PurchaseResponse, AssetSource, SupplierSelection, OrderItem, RetirementDetails,
    CarbonmarkOrderRequest, CarbonmarkOrderResponse, QuoteStorage, OrderHistory
)
from app.auth_service import create_user, authenticate_user

# Load environment variables
load_dotenv()

# In-memory quote storage (in production, use database)
quote_storage = {}


BLOCKCHAIN_API_URL = os.getenv("BLOCKCHAIN_API_URL")
ETH2DOLLAR = float(os.getenv("ETH2DOLLAR"))

app = FastAPI(title="CarbonChain API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Mount static directory (if needed for assets)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    pass  # Directory doesn't exist yet

# Set up templates directory
try:
    templates = Jinja2Templates(directory="templates")
except:
    templates = None

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return HTMLResponse("<h1>CarbonChain API</h1><p>API is running. Visit /docs for API documentation.</p>")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "carbonchain-api"}

# --- AUTHENTICATION ENDPOINTS ---
@app.post("/signup", response_model=UserResponse)
async def signup(user_data: UserSignup):
    """Create a new user account"""
    try:
        user = await create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create user account")

@app.post("/login", response_model=UserResponse)
async def login(credentials: UserLogin):
    """Authenticate user and return user data"""
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user

# --- COUNTRIES ENDPOINT ---
@app.get("/search_countries")
async def search_countries():
    try:
        response = requests.get("https://v17.api.carbonmark.com/countries")
        response.raise_for_status()
        data = response.json()
        # Unpack the JSON to return a list of country names
        countries = [country["id"] for country in data]
        return JSONResponse(content={"countries": countries})
    except requests.RequestException as e:
        return JSONResponse(content={"error": "Failed to fetch countries"}, status_code=500)
    
# --- METHODOLOGIES ENDPOINT ---
@app.get("/search_categories")
async def search_categories():
    try:
        response = requests.get("https://v17.api.carbonmark.com/categories")
        response.raise_for_status()
        data = response.json()
        # Unpack the JSON to return a list of category names
        categories = [category["id"] for category in data]
        return JSONResponse(content={"categories": categories})
    except requests.RequestException as e:
        return JSONResponse(content={"error": "Failed to fetch categories"}, status_code=500)

# --- SEARCH ENDPOINT ---
@app.get("/search")
async def search_projects(
	country: str = Query(None),
	methodology: str = Query(None),
	name: str = Query(None)
    ):
	parameters = {"limit": 100, "minSupply": 1}
	if country: parameters['country'] = country
	if methodology: parameters['category'] = methodology
	if name: parameters['name'] = name
	# Stub: return dummy data
	result = requests.get("https://v17.api.carbonmark.com/carbonProjects", params=parameters)

	return JSONResponse(content=result.json())

# --- SUPPLIER SELECTION HELPER FUNCTION ---
async def get_asset_prices_and_select_suppliers(project_id: str, quantity: float, expected_cost: float):
    """
    Two-phase supplier selection approach:
    1. First try to find a single supplier with minSupply=quantity that meets cost requirements
    2. If unsuccessful, fall back to multi-supplier optimization
    """
    try:
        # Get API key from environment
        carbonmark_api_key = os.getenv("CARBONMARK_API_KEY")
        if not carbonmark_api_key:
            raise Exception("Carbonmark API key not configured")
        
        headers = {
            "Authorization": f"Bearer {carbonmark_api_key}",
            "Content-Type": "application/json"
        }
        
        print(f"Starting two-phase supplier selection for project: {project_id}")
        print(f"Requested quantity: {quantity}, Expected cost: ${expected_cost:.2f}")
        
        # PHASE 1: Try to find a single supplier that can fulfill the entire order
        print("\n=== PHASE 1: Single supplier search ===")
        print(f"Looking for suppliers with at least {quantity} tons in stock...")
        
        phase1_response = requests.get(
            f"https://api.carbonmark.com/prices?project={project_id}&minSupply={quantity}",
            headers=headers
        )
        
        print(f"Phase 1 API Response Status: {phase1_response.status_code}")
        
        if phase1_response.ok:
            phase1_data = phase1_response.json()
            print(f"Phase 1 raw response: {phase1_data}")
            print(f"Phase 1 response structure: {type(phase1_data)}")
            if isinstance(phase1_data, list) and len(phase1_data) > 0:
                print(f"First item structure: {phase1_data[0]}")
                print(f"First item keys: {list(phase1_data[0].keys()) if isinstance(phase1_data[0], dict) else 'Not a dict'}")
            elif isinstance(phase1_data, dict):
                print(f"Dict keys: {list(phase1_data.keys())}")
            
            # Parse Phase 1 sources
            phase1_sources = parse_sources_from_response(phase1_data)
            print(f"Phase 1 found {len(phase1_sources)} suppliers with sufficient stock")
            
            # Filter by cost constraint and find the best single supplier
            viable_single_suppliers = []
            for source in phase1_sources:
                total_cost_for_quantity = source.purchasePrice * quantity
                if total_cost_for_quantity <= expected_cost:
                    viable_single_suppliers.append((source, total_cost_for_quantity))
                    print(f"  Viable supplier: {source.sourceId} - ${source.purchasePrice}/ton, total cost: ${total_cost_for_quantity:.2f}")
            
            if viable_single_suppliers:
                # Sort by total cost and pick the cheapest
                viable_single_suppliers.sort(key=lambda x: x[1])
                best_supplier, best_cost = viable_single_suppliers[0]
                
                print(f"✓ Phase 1 SUCCESS: Found optimal single supplier")
                print(f"  Supplier: {best_supplier.sourceId}")
                print(f"  Price per ton: ${best_supplier.purchasePrice:.2f}")
                print(f"  Total cost: ${best_cost:.2f}")
                
                # Create the selection with just this one supplier
                selected_source = AssetSource(
                    sourceId=best_supplier.sourceId,
                    purchasePrice=best_supplier.purchasePrice,
                    supply=quantity,  # Use the exact quantity we need
                    poolName=best_supplier.poolName,
                    assetPriceSourceId=best_supplier.assetPriceSourceId,
                    listingId=best_supplier.listingId,
                    pool=best_supplier.pool
                )
                
                return SupplierSelection(
                    selectedSources=[selected_source],
                    totalCost=best_cost,
                    totalSupply=quantity,
                    canFulfillQuantity=True,
                    costExceedsExpected=False
                )
            else:
                print("✗ Phase 1 FAILED: No single supplier meets cost constraint")
                # If no viable suppliers found in Phase 1, check if we even found any sources
                if len(phase1_sources) == 0:
                    print("✗ Phase 1 FAILED: No sources found in API response")
        else:
            print(f"✗ Phase 1 FAILED: API error {phase1_response.status_code}")
        
        # PHASE 2: Multi-supplier fallback
        print(f"\n=== PHASE 2: Multi-supplier optimization ===")
        print("Searching for multiple suppliers to combine orders...")
        
        phase2_response = requests.get(
            f"https://api.carbonmark.com/prices?project={project_id}",
            headers=headers
        )
        
        print(f"Phase 2 API Response Status: {phase2_response.status_code}")
        
        if not phase2_response.ok:
            error_detail = f"Both phases failed. Phase 2 API error: {phase2_response.status_code}"
            try:
                error_data = phase2_response.json()
                error_detail += f" - {error_data.get('message', 'Unknown error')}"
                print(f"API Error Response: {error_data}")
            except:
                error_detail += f" - {phase2_response.text}"
                print(f"API Error Text: {phase2_response.text}")
            raise Exception(error_detail)
        
        phase2_data = phase2_response.json()
        print(f"Phase 2 raw response: {phase2_data}")
        print(f"Phase 2 response structure: {type(phase2_data)}")
        if isinstance(phase2_data, list) and len(phase2_data) > 0:
            print(f"First item structure: {phase2_data[0]}")
            print(f"First item keys: {list(phase2_data[0].keys()) if isinstance(phase2_data[0], dict) else 'Not a dict'}")
        elif isinstance(phase2_data, dict):
            print(f"Dict keys: {list(phase2_data.keys())}")
        
        # Parse Phase 2 sources
        all_sources = parse_sources_from_response(phase2_data)
        print(f"Phase 2 found {len(all_sources)} total suppliers")
        
        if not all_sources:
            raise Exception("Issue returning listing - No asset sources found for this project")
        
        # Multi-supplier optimization: sort by price and combine optimally
        all_sources.sort(key=lambda x: x.purchasePrice)
        
        selected_sources = []
        total_supply = 0.0
        total_cost = 0.0
        
        for source in all_sources:
            if total_supply >= quantity:
                break
            
            # Calculate how much we need from this source
            needed_quantity = min(source.supply, quantity - total_supply)
            
            if needed_quantity > 0:
                selected_source = AssetSource(
                    sourceId=source.sourceId,
                    purchasePrice=source.purchasePrice,
                    supply=needed_quantity,
                    poolName=source.poolName,
                    assetPriceSourceId=source.assetPriceSourceId,
                    listingId=source.listingId,
                    pool=source.pool
                )
                selected_sources.append(selected_source)
                
                total_supply += needed_quantity
                total_cost += needed_quantity * source.purchasePrice
                
                print(f"  Added supplier: {source.sourceId} - {needed_quantity} tons @ ${source.purchasePrice}/ton")
        
        # Final results
        can_fulfill_quantity = total_supply >= quantity
        cost_exceeds_expected = total_cost > expected_cost
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"Phase used: Multi-supplier (Phase 2)")
        print(f"Suppliers selected: {len(selected_sources)}")
        print(f"Total supply: {total_supply} tons")
        print(f"Total cost: ${total_cost:.2f}")
        print(f"Expected cost: ${expected_cost:.2f}")
        print(f"Can fulfill quantity: {can_fulfill_quantity}")
        print(f"Cost exceeds expected: {cost_exceeds_expected}")
        
        if cost_exceeds_expected and can_fulfill_quantity:
            print("Note: Cost exceeds expected but quantity fulfilled as requested")
        
        return SupplierSelection(
            selectedSources=selected_sources,
            totalCost=total_cost,
            totalSupply=total_supply,
            canFulfillQuantity=can_fulfill_quantity,
            costExceedsExpected=cost_exceeds_expected
        )
        
    except Exception as e:
        print(f"Error in supplier selection: {str(e)}")
        raise


def parse_sources_from_response(prices_data):
    """
    Helper function to parse asset sources from Carbonmark API response.
    Handles multiple response formats.
    """
    sources = []
    
    if isinstance(prices_data, list):
        for item in prices_data:
            print(f"Processing item: {item}")
            print(f"Item keys: {list(item.keys()) if isinstance(item, dict) else 'Not a dict'}")
            
            # Check for direct Carbonmark API format (sourceId, purchasePrice, supply)
            if 'sourceId' in item and 'purchasePrice' in item and 'supply' in item:
                pool_name = ""
                # Extract pool name from carbonPool if available
                if 'carbonPool' in item and 'poolName' in item['carbonPool']:
                    pool_name = item['carbonPool']['poolName']
                elif 'poolName' in item:
                    pool_name = item['poolName']
                
                sources.append(AssetSource(
                    sourceId=item.get('sourceId', ''),
                    purchasePrice=float(item.get('purchasePrice', 0)),
                    supply=float(item.get('supply', 0)),
                    poolName=pool_name,
                    assetPriceSourceId=item.get('id') or item.get('assetPriceSourceId'),  # This might be the 'id' field
                    listingId=item.get('listingId'),
                    pool=item.get('pool') or pool_name
                ))
                print(f"  Added source: {item.get('sourceId')} - ${item.get('purchasePrice')}/ton, {item.get('supply')} tons")
                print(f"    Additional fields: assetPriceSourceId={item.get('id')}, listingId={item.get('listingId')}, pool={item.get('pool') or pool_name}")
            
            # Legacy format: Direct source format with 'id', 'price', 'supply'
            elif 'id' in item and 'price' in item and 'supply' in item:
                sources.append(AssetSource(
                    sourceId=item.get('id', ''),
                    purchasePrice=float(item.get('price', 0)),
                    supply=float(item.get('supply', 0)),
                    poolName=item.get('poolName', item.get('pool', '')),
                    assetPriceSourceId=item.get('id'),  # Use the id as assetPriceSourceId
                    listingId=item.get('listingId'),
                    pool=item.get('pool') or item.get('poolName', '')
                ))
                print(f"  Added legacy source: {item.get('id')} - ${item.get('price')}/ton, {item.get('supply')} tons")
                print(f"    Additional fields: assetPriceSourceId={item.get('id')}, listingId={item.get('listingId')}, pool={item.get('pool') or item.get('poolName', '')}")
            
            # Nested sources format
            elif 'sources' in item:
                for source in item.get('sources', []):
                    if 'sourceId' in source and 'purchasePrice' in source and 'supply' in source:
                        sources.append(AssetSource(
                            sourceId=source.get('sourceId', ''),
                            purchasePrice=float(source.get('purchasePrice', 0)),
                            supply=float(source.get('supply', 0)),
                            poolName=source.get('poolName', ''),
                            assetPriceSourceId=source.get('id') or source.get('assetPriceSourceId'),
                            listingId=source.get('listingId'),
                            pool=source.get('pool') or source.get('poolName', '')
                        ))
                    elif 'id' in source and 'price' in source and 'supply' in source:
                        sources.append(AssetSource(
                            sourceId=source.get('id', ''),
                            purchasePrice=float(source.get('price', 0)),
                            supply=float(source.get('supply', 0)),
                            poolName=source.get('poolName', source.get('pool', '')),
                            assetPriceSourceId=source.get('id'),
                            listingId=source.get('listingId'),
                            pool=source.get('pool') or source.get('poolName', '')
                        ))
    
    elif isinstance(prices_data, dict):
        # Sources array in dict
        if 'sources' in prices_data:
            for source in prices_data.get('sources', []):
                if 'sourceId' in source and 'purchasePrice' in source and 'supply' in source:
                    sources.append(AssetSource(
                        sourceId=source.get('sourceId', ''),
                        purchasePrice=float(source.get('purchasePrice', 0)),
                        supply=float(source.get('supply', 0)),
                        poolName=source.get('poolName', '')
                    ))
                elif 'id' in source and 'price' in source and 'supply' in source:
                    sources.append(AssetSource(
                        sourceId=source.get('id', ''),
                        purchasePrice=float(source.get('price', 0)),
                        supply=float(source.get('supply', 0)),
                        poolName=source.get('poolName', source.get('pool', ''))
                    ))
        
        # Dict is itself a source (Carbonmark format)
        elif 'sourceId' in prices_data and 'purchasePrice' in prices_data and 'supply' in prices_data:
            pool_name = ""
            if 'carbonPool' in prices_data and 'poolName' in prices_data['carbonPool']:
                pool_name = prices_data['carbonPool']['poolName']
            elif 'poolName' in prices_data:
                pool_name = prices_data['poolName']
                
            sources.append(AssetSource(
                sourceId=prices_data.get('sourceId', ''),
                purchasePrice=float(prices_data.get('purchasePrice', 0)),
                supply=float(prices_data.get('supply', 0)),
                poolName=pool_name,
                assetPriceSourceId=prices_data.get('id') or prices_data.get('assetPriceSourceId'),
                listingId=prices_data.get('listingId'),
                pool=prices_data.get('pool') or pool_name
            ))
        
        # Legacy dict format
        elif 'id' in prices_data and 'price' in prices_data and 'supply' in prices_data:
            sources.append(AssetSource(
                sourceId=prices_data.get('id', ''),
                purchasePrice=float(prices_data.get('price', 0)),
                supply=float(prices_data.get('supply', 0)),
                poolName=prices_data.get('poolName', prices_data.get('pool', '')),
                assetPriceSourceId=prices_data.get('id'),
                listingId=prices_data.get('listingId'),
                pool=prices_data.get('pool') or prices_data.get('poolName', '')
            ))
        
        # Data section
        elif 'data' in prices_data:
            data_section = prices_data['data']
            if isinstance(data_section, list):
                for item in data_section:
                    if 'sourceId' in item and 'purchasePrice' in item and 'supply' in item:
                        sources.append(AssetSource(
                            sourceId=item.get('sourceId', ''),
                            purchasePrice=float(item.get('purchasePrice', 0)),
                            supply=float(item.get('supply', 0)),
                            poolName=item.get('poolName', '')
                        ))
                    elif 'id' in item and 'price' in item and 'supply' in item:
                        sources.append(AssetSource(
                            sourceId=item.get('id', ''),
                            purchasePrice=float(item.get('price', 0)),
                            supply=float(item.get('supply', 0)),
                            poolName=item.get('poolName', item.get('pool', ''))
                        ))
    
    return sources

# --- CARBONMARK QUOTE GENERATION HELPER ---
async def generate_carbonmark_quote(selected_sources: list[AssetSource], retirement_details: dict):
    """
    Generate a quote with Carbonmark API using selected sources
    """
    try:
        carbonmark_api_key = os.getenv("CARBONMARK_API_KEY")
        if not carbonmark_api_key:
            raise Exception("Carbonmark API key not configured")
        
        headers = {
            "Authorization": f"Bearer {carbonmark_api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare quote request for Carbonmark - try different structures
        source = selected_sources[0]  # Use the first source
        
        # Try format 1: Direct fields with correct field names
        quote_request_v1 = {
            "asset_price_source_id": source.assetPriceSourceId or source.sourceId,
            "listing_id": source.listingId or source.sourceId,
            "pool": source.pool or source.poolName or "default",
            "quantity_tonnes": str(source.supply),  # Use quantity_tonnes instead of quantity
            "retirementDetails": retirement_details
        }
        
        # Try format 2: Items array with correct field names
        quote_request_v2 = {
            "items": [{
                "asset_price_source_id": source.assetPriceSourceId or source.sourceId,
                "listing_id": source.listingId or source.sourceId,
                "pool": source.pool or source.poolName or "default", 
                "quantity_tonnes": str(source.supply)  # Use quantity_tonnes instead of quantity
            }],
            "retirementDetails": retirement_details
        }
        
        # Try format 3: CamelCase field names with correct quantity field
        quote_request_v3 = {
            "assetPriceSourceId": source.assetPriceSourceId or source.sourceId,
            "listingId": source.listingId or source.sourceId,
            "pool": source.pool or source.poolName or "default",
            "quantityTonnes": str(source.supply),  # Use quantityTonnes in camelCase
            "retirementDetails": retirement_details
        }
        
        # Try format 4: Just the essential fields as per error message
        quote_request_v4 = {
            "asset_price_source_id": source.assetPriceSourceId or source.sourceId,
            "listing_id": source.listingId or source.sourceId,
            "quantity_tonnes": str(source.supply)
        }
        
        # Start with format 1
        quote_request = quote_request_v1
        
        print(f"Generating Carbonmark quote for single item")
        print(f"Quote request payload (format 1): {quote_request}")
        
        # Try format 1 first
        quote_response = requests.post(
            "https://api.carbonmark.com/quotes",
            headers=headers,
            json=quote_request,
            timeout=30
        )
        
        print(f"Carbonmark quote API response status (format 1): {quote_response.status_code}")
        
        # If format 1 fails, try format 2
        if not quote_response.ok:
            print("Format 1 failed, trying format 2 (items array)...")
            quote_request = quote_request_v2
            print(f"Quote request payload (format 2): {quote_request}")
            
            quote_response = requests.post(
                "https://api.carbonmark.com/quotes", 
                headers=headers,
                json=quote_request,
                timeout=30
            )
            
            print(f"Carbonmark quote API response status (format 2): {quote_response.status_code}")
        
        # If format 2 fails, try format 3
        if not quote_response.ok:
            print("Format 2 failed, trying format 3 (camelCase fields)...")
            quote_request = quote_request_v3
            print(f"Quote request payload (format 3): {quote_request}")
            
            quote_response = requests.post(
                "https://api.carbonmark.com/quotes",
                headers=headers, 
                json=quote_request,
                timeout=30
            )
            
            print(f"Carbonmark quote API response status (format 3): {quote_response.status_code}")
        
        # If format 3 fails, try format 4 (minimal fields only)
        if not quote_response.ok:
            print("Format 3 failed, trying format 4 (minimal fields only)...")
            quote_request = quote_request_v4
            print(f"Quote request payload (format 4): {quote_request}")
            
            quote_response = requests.post(
                "https://api.carbonmark.com/quotes",
                headers=headers, 
                json=quote_request,
                timeout=30
            )
            
            print(f"Carbonmark quote API response status (format 4): {quote_response.status_code}")
        
        if not quote_response.ok:
            error_detail = f"Carbonmark quote API error: {quote_response.status_code}"
            try:
                error_data = quote_response.json()
                error_detail += f" - {error_data.get('message', 'Unknown error')}"
                print(f"Carbonmark Quote API Error: {error_data}")
            except:
                error_detail += f" - {quote_response.text}"
                print(f"Carbonmark Quote API Error Text: {quote_response.text}")
            raise Exception(error_detail)
        
        quote_data = quote_response.json()
        print(f"Carbonmark quote generated successfully: {quote_data}")
        
        # Return the quote UUID - based on actual response format
        quote_uuid = (quote_data.get('uuid') or 
                     quote_data.get('quote_uuid') or 
                     quote_data.get('quoteId') or 
                     quote_data.get('id'))
        
        print(f"Extracted quote UUID: {quote_uuid}")
        return quote_uuid
        
    except Exception as e:
        print(f"Error generating Carbonmark quote: {str(e)}")
        # Don't fail completely - we can still proceed without Carbonmark quote UUID
        # but order execution may fail
        return None

# --- GET QUOTE ENDPOINT ---
@app.post("/get_quote")
async def get_quote(purchase_request: PurchaseRequest):
    """
    Get a quote for carbon credit purchase without executing the purchase.
    This endpoint provides supplier selection and pricing information.
    """
    try:
        # Log the quote request for debugging
        print(f"Received quote request for project {purchase_request.projectId}")
        print(f"Quantity: {purchase_request.quantity} tons CO2")
        print(f"Expected Total Cost: ${purchase_request.totalCost}")
        
        # Validate the quote request
        if purchase_request.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        
        # Fetch asset prices and select suppliers
        try:
            supplier_selection = await get_asset_prices_and_select_suppliers(
                purchase_request.projectId,
                purchase_request.quantity,
                purchase_request.totalCost
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to fetch asset prices or select suppliers: {str(e)}"
            )
        
        # Check if we can fulfill the request
        if not supplier_selection.canFulfillQuantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient supply available. Requested: {purchase_request.quantity}, Available: {supplier_selection.totalSupply}"
            )
        
        # Generate a quote ID for tracking
        import uuid
        quote_id = str(uuid.uuid4())
        
        # Store the quote for later validation during order execution
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Quote valid for 1 hour
        
        quote_storage[quote_id] = QuoteStorage(
            quoteId=quote_id,
            carbonmarkQuoteId=None,  # Will be generated during purchase execution
            projectId=purchase_request.projectId,
            quantity=purchase_request.quantity,
            selectedSources=supplier_selection.selectedSources,
            totalCost=supplier_selection.totalCost,
            createdAt=datetime.utcnow(),
            expiresAt=expires_at,
            status="active"
        )
        
        # Prepare quote data
        quote_data = {
            "quoteId": quote_id,
            "projectId": purchase_request.projectId,
            "projectName": purchase_request.projectData.name,
            "quantity": purchase_request.quantity,
            "expectedCost": purchase_request.totalCost,
            "actualCost": supplier_selection.totalCost,
            "costExceedsExpected": supplier_selection.costExceedsExpected,
            "validUntil": datetime.utcnow().isoformat() + "Z",  # Quote valid for implementation
            "selectedSources": [
                {
                    "sourceId": source.sourceId,
                    "poolName": source.poolName,
                    "quantity": source.supply,
                    "pricePerTon": source.purchasePrice,
                    "totalCost": source.supply * source.purchasePrice
                }
                for source in supplier_selection.selectedSources
            ],
            "status": "quote_ready"
        }
        
        # Determine appropriate message
        if supplier_selection.costExceedsExpected:
            message = f"Quote generated successfully. Note: Actual cost (${supplier_selection.totalCost:.2f}) exceeds expected cost (${purchase_request.totalCost:.2f})."
        else:
            message = f"Quote generated successfully. Total cost: ${supplier_selection.totalCost:.2f}"
        
        # Return quote response
        return {
            "success": True,
            "message": message,
            "quoteId": quote_id,
            "timestamp": datetime.utcnow(),
            "quote": quote_data,
            "supplierSelection": supplier_selection
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Quote error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while generating the quote: {str(e)}"
        )

# --- PURCHASE ENDPOINT ---
@app.post("/purchase", response_model=PurchaseResponse)
async def execute_purchase(confirmation_request: PurchaseConfirmationRequest):
    """
    Execute carbon credit purchase based on a confirmed quote.
    This calls the Carbonmark API to place the actual order.
    """
    try:
        # Log the purchase confirmation
        print(f"Received purchase confirmation for quote: {confirmation_request.quoteId}")
        print(f"Certificate: {confirmation_request.certificateFirstName} {confirmation_request.certificateLastName}")
        print(f"Message: {confirmation_request.retirementMessage}")
        print(f"User: {confirmation_request.userId}")

        # Extract project information from request
        project_id = confirmation_request.projectId
        project_name = confirmation_request.projectName
        project_url = confirmation_request.projectUrl
        project_registry = confirmation_request.projectRegistry
        
        print(f"Project details: ID={project_id}, Name={project_name}, URL={project_url}, Registry={project_registry}")

        # Validate the confirmation request
        if not confirmation_request.certificateFirstName.strip() or not confirmation_request.certificateLastName.strip():
            raise HTTPException(status_code=400, detail="Certificate name is required")
        
        if not confirmation_request.retirementMessage.strip():
            raise HTTPException(status_code=400, detail="Retirement message is required")
        
        # Retrieve and validate the quote
        if confirmation_request.quoteId not in quote_storage:
            raise HTTPException(status_code=404, detail="Quote not found or expired")
        
        stored_quote = quote_storage[confirmation_request.quoteId]
        
        # Check if quote has expired
        if datetime.utcnow() > stored_quote.expiresAt:
            # Clean up expired quote
            del quote_storage[confirmation_request.quoteId]
            raise HTTPException(status_code=400, detail="Quote has expired. Please generate a new quote.")
        
        # Check if quote is still active
        if stored_quote.status != "active":
            raise HTTPException(status_code=400, detail="Quote is no longer valid")
        
        print(f"Quote validated: {stored_quote.quoteId} for project {stored_quote.projectId}")
        
        # Get Carbonmark API key
        carbonmark_api_key = os.getenv("CARBONMARK_API_KEY")
        if not carbonmark_api_key:
            raise HTTPException(status_code=500, detail="Carbonmark API key not configured")
        
        # Prepare retirement details for Carbonmark quote
        full_name = f"{confirmation_request.certificateFirstName.strip()} {confirmation_request.certificateLastName.strip()}"
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        retirement_details = {
            "retiringEntityName": full_name,
            "retirementMessage": confirmation_request.retirementMessage.strip(),
            "consumptionCountryCode": "US",
            "consumptionPeriodStart": current_date,
            "consumptionPeriodEnd": current_date
        }
        
        # Generate Carbonmark quote UUID if we don't have one
        if not stored_quote.carbonmarkQuoteId:
            print("Generating Carbonmark quote for order execution...")
            carbonmark_quote_id = await generate_carbonmark_quote(stored_quote.selectedSources, retirement_details)
            if not carbonmark_quote_id:
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to generate Carbonmark quote. Order cannot be executed."
                )
            stored_quote.carbonmarkQuoteId = carbonmark_quote_id
            print(f"Generated Carbonmark quote ID: {carbonmark_quote_id}")
        
        # Create proper order request as per Carbonmark API docs
        print(f"Creating order request with quote UUID: {stored_quote.carbonmarkQuoteId}")
        
        # Validate required fields before creating request
        if not stored_quote.carbonmarkQuoteId:
            raise HTTPException(status_code=500, detail="Missing Carbonmark quote UUID")
        if not full_name or len(full_name.strip()) < 1:
            raise HTTPException(status_code=400, detail="Beneficiary name is required and must be at least 1 character")
        if not confirmation_request.retirementMessage.strip() or len(confirmation_request.retirementMessage.strip()) < 1:
            raise HTTPException(status_code=400, detail="Retirement message is required and must be at least 1 character")
        
        # Order request matching API documentation format
        order_request_data = {
            "quote_uuid": stored_quote.carbonmarkQuoteId,
            "beneficiary_name": full_name[:255],  # Truncate to max 255 chars
            "retirement_message": confirmation_request.retirementMessage.strip()[:500],  # Truncate to max 500 chars
            "consumption_metadata": {
                "country_of_consumption_code": "string", #placeholders, we dont care abt this
                "consumption_period_start": 0,
                "consumption_period_end": 0
            }
        }
        # Note: beneficiary_address is optional, so we're omitting it
        
        print(f"Order request created: {order_request_data}")
        print(f"Field validation:")
        print(f"  - quote_uuid: {len(stored_quote.carbonmarkQuoteId)} chars")
        print(f"  - beneficiary_name: '{full_name[:255]}' ({len(full_name)} chars)")
        print(f"  - retirement_message: '{confirmation_request.retirementMessage.strip()[:50]}...' ({len(confirmation_request.retirementMessage.strip())} chars)")
        print(f"  - country_code: US")
        print(f"  - consumption_period: {int(datetime.utcnow().timestamp())}")
        
        print(f"Sending order to Carbonmark API using quote UUID: {stored_quote.carbonmarkQuoteId}")
        print(f"Order request data: {order_request_data}")
        
        # Execute order with Carbonmark API
        headers = {
            "Authorization": f"Bearer {carbonmark_api_key}",
            "Content-Type": "application/json"
        }
        
        # Send the order request
        try:
            carbonmark_response = requests.post(
                "https://v17.api.carbonmark.com/orders",  # Using v17 endpoint as per documentation
                headers=headers,
                json=order_request_data,
                timeout=30
            )
            
            print(f"Carbonmark orders API response status: {carbonmark_response.status_code}")
            print(f"Carbonmark orders API response headers: {dict(carbonmark_response.headers)}")
        
        except requests.exceptions.RequestException as req_error:
            print(f"Request error when calling Carbonmark orders API: {req_error}")
            raise HTTPException(
                status_code=502,
                detail=f"Network error when calling Carbonmark API: {str(req_error)}"
            )
        
        if not carbonmark_response.ok:
            error_detail = f"Carbonmark API error: {carbonmark_response.status_code}"
            error_response_text = ""
            
            try:
                error_data = carbonmark_response.json()
                error_detail += f" - {error_data.get('message', error_data.get('detail', 'Unknown error'))}"
                print(f"Carbonmark API Error Response: {error_data}")
                
                # Log specific validation errors if available
                if 'errors' in error_data:
                    print(f"Validation errors: {error_data['errors']}")
                if 'details' in error_data:
                    print(f"Error details: {error_data['details']}")
                    
                error_response_text = str(error_data)
            except Exception as json_error:
                error_response_text = carbonmark_response.text
                error_detail += f" - {error_response_text}"
                print(f"Carbonmark API Error Text: {error_response_text}")
                print(f"JSON parsing error: {json_error}")
            
            print(f"Request that failed:")
            print(f"  URL: https://v17.api.carbonmark.com/orders")
            print(f"  Headers: {headers}")
            print(f"  Body: {order_request_data}")
            
            raise HTTPException(
                status_code=502,
                detail=f"Failed to execute order with Carbonmark: {error_detail}"
            )
        
        # Parse Carbonmark response
        carbonmark_data = carbonmark_response.json()
        print(f"Carbonmark order executed successfully: {carbonmark_data}")
        
        # Create response object - mapping the actual order response format
        try:
            # Extract fields from the actual order response structure
            order_id = carbonmark_data.get('quote', {}).get('uuid') or carbonmark_data.get('id', 'unknown')
            order_status = carbonmark_data.get('status', 'SUBMITTED')
            created_at = carbonmark_data.get('created_at', str(datetime.utcnow()))
            updated_at = carbonmark_data.get('updated_at', str(datetime.utcnow()))
            
            # Extract quote data
            quote_data = carbonmark_data.get('quote', {})
            total_quantity = str(quote_data.get('quantity_tonnes', stored_quote.quantity))
            total_price = str(quote_data.get('cost_usdc', stored_quote.totalCost))
            
            carbonmark_order = CarbonmarkOrderResponse(
                orderId=order_id,
                orderStatus=order_status,
                items=[],  # Items are embedded in quote data
                createdAt=created_at,
                updatedAt=updated_at,
                totalCarbonQuantity=total_quantity,
                totalPrice=total_price,
                retirementDetails=carbonmark_data.get('consumption_metadata')
            )
            print(f"Successfully parsed Carbonmark response into model")
            
        except Exception as parse_error:
            print(f"Error parsing Carbonmark response: {parse_error}")
            print(f"Response data structure: {carbonmark_data}")
            
            # Create a basic response with available data
            carbonmark_order = CarbonmarkOrderResponse(
                orderId=str(carbonmark_data.get('quote', {}).get('uuid', 'unknown')),
                orderStatus=carbonmark_data.get('status', 'SUBMITTED'),
                items=[],
                createdAt=str(datetime.utcnow()),
                updatedAt=str(datetime.utcnow()),
                totalCarbonQuantity=str(stored_quote.quantity),
                totalPrice=str(stored_quote.totalCost),
                retirementDetails=None
            )
        
        # Mark quote as used
        stored_quote.status = "used"
        
        # Save order to history database
        full_certificate_name = f"{confirmation_request.certificateFirstName.strip()} {confirmation_request.certificateLastName.strip()}"
        
        try:
            # Create order history record
            order_history_data = {
                "user_id": confirmation_request.userId,
                "order_id": carbonmark_order.orderId,
                "quote_id": confirmation_request.quoteId,
                "carbonmark_quote_id": stored_quote.carbonmarkQuoteId,
                "project_id": stored_quote.projectId,
                "project_name": project_name,  # Use project name from request
                "quantity": stored_quote.quantity,
                "total_cost": stored_quote.totalCost,
                "certificate_name": full_certificate_name,
                "retirement_message": confirmation_request.retirementMessage.strip(),
                "order_status": carbonmark_order.orderStatus,
                "created_at": datetime.utcnow(),
                "carbonmark_response": carbonmark_data,  # Store the full Carbonmark response
                "sources": stored_quote.selectedSources  # Add sources for blockchain save
            }
            
            # Save to database
            history_id = await save_order_to_history(order_history_data)
            print(f"Order saved to history with ID: {history_id}")

            # Save to blockchain with project data
            blockchain_record = await save_order_to_blockchain(
                order_history_data, 
                project_id, 
                project_name, 
                project_url, 
                project_registry,
                confirmation_request.userId
            )
            print(f"Order saved to blockchain: {blockchain_record}")
            
        except Exception as save_error:
            # Don't fail the order if we can't save to history
            print(f"Warning: Failed to save order to history: {save_error}")
        
        # Prepare successful response
        full_certificate_name = f"{confirmation_request.certificateFirstName.strip()} {confirmation_request.certificateLastName.strip()}"
        
        return PurchaseResponse(
            success=True,
            message=f"Carbon credit purchase completed successfully! Order ID: {carbonmark_order.orderId}",
            orderId=carbonmark_order.orderId,
            timestamp=datetime.utcnow(),
            data={
                "quoteId": confirmation_request.quoteId,
                "carbonmarkQuoteId": stored_quote.carbonmarkQuoteId,
                "projectId": stored_quote.projectId,
                "status": "completed",
                "certificateName": full_certificate_name,
                "retirementMessage": confirmation_request.retirementMessage,
                "totalCarbonQuantity": carbonmark_order.totalCarbonQuantity,
                "totalPrice": carbonmark_order.totalPrice,
                "orderStatus": carbonmark_order.orderStatus,
                "createdAt": carbonmark_order.createdAt,
                "sourceCount": len(stored_quote.selectedSources),
                "sources": stored_quote.selectedSources,
                "executionTimestamp": datetime.utcnow().isoformat()
            },
            carbonmarkOrder=carbonmark_order
        )
        
    except HTTPException:
        raise
    except requests.RequestException as e:
        print(f"Network error during order execution: {str(e)}")
        raise HTTPException(
            status_code=502, 
            detail=f"Network error while executing order: {str(e)}"
        )
    except Exception as e:
        print(f"Purchase execution error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while executing the purchase: {str(e)}"
        )

async def save_order_to_blockchain(order_data: dict, project_id: str, project_name: str, project_url: str, project_registry: str, user_id: str):
    """
    Save order data to blockchain with proper user email lookup
    """
    try:
        # Get user details from database to extract email
        user = await get_user_by_id(user_id)
        funder_email = user.get('email', 'unknown@email.com') if user else user_id
        
        print(f"Blockchain save - User lookup: {user_id} -> {funder_email}")
        
        # Get supplier names from selected sources for beneficiary_id
        sources = order_data.get("sources", [])
        if isinstance(sources, list) and len(sources) > 0:
            # Use the first supplier's pool name or source ID
            first_source = sources[0]
            if hasattr(first_source, 'poolName') and first_source.poolName:
                beneficiary_id = first_source.poolName
            elif hasattr(first_source, 'sourceId'):
                beneficiary_id = first_source.sourceId
            else:
                beneficiary_id = "UNKNOWN_SUPPLIER"
        else:
            beneficiary_id = "UNKNOWN_SUPPLIER"
        if not project_registry:
            project_registry = "UNKNOWN_REGISTRY"

        if await get_user_by_id(f"{beneficiary_id}@{beneficiary_id}.com") is None:
            try:
                await create_user(UserSignup(
                    email=f"{beneficiary_id}@{beneficiary_id}.com",
                    password="supplier",
                    first_name=beneficiary_id,
                    last_name="supplier"
                ))
            except ValueError as error:
                pass


        if await get_user_by_id(f"{project_registry}@{project_registry}.com") is None:
            try:
                await create_user(UserSignup(
                    email=f"{project_registry}@{project_registry}.com",
                    password="registry",
                    first_name=project_registry,
                    last_name="registry"
                ))
            except ValueError as error:
                pass

        amount = float(order_data.get("quantity", 0))
        amount /= ETH2DOLLAR
        # Create blockchain record with proper data
        order_record = {
            "proposer_id": funder_email,  # User's email from database
            "beneficiary_id": f"{beneficiary_id}@{beneficiary_id}.com",  # Supplier pool/source name
            "verifier_id": f"{project_registry}@{project_registry}.com",
            "initiative": project_name or "Unknown Project",
            "metadata_uri": project_url or "https://dayof.pennapps.com/",
            "goal": amount  # Convert to float
        }
        

        print(f"Blockchain record created: {order_record}")

        response = requests.post(f"{BLOCKCHAIN_API_URL}/propose", json=order_record)
        response.raise_for_status()

        # Get the newly created project address
        projects_response = requests.get(f"{BLOCKCHAIN_API_URL}/projects")
        projects = projects_response.json()["projects"]
        project_address = projects[-1]  # Get the latest project

        funder_payload = {
            "user_id": funder_email,
            "project_address": project_address,
            "amount": str(amount)
        }
        print(project_address)

        response = requests.post(f"{BLOCKCHAIN_API_URL}/fund", json=funder_payload)
        response.raise_for_status()

        verify_payload = {
            "verifier_id": f"{project_registry}@{project_registry}.com",
            "project_address": project_address,
        }

        response = requests.post(f"{BLOCKCHAIN_API_URL}/verify", json=verify_payload)
        response.raise_for_status()
        print("Funding successful")

        return order_record
        
    except Exception as e:
        print(f"Error creating blockchain record: {e}")
        # Return fallback record
        return {
            "proposer_id": user_id or "UNKNOWN_USER",
            "beneficiary_id": "UNKNOWN_SUPPLIER", 
            "verifier_id": project_registry or "Unknown Registry",
            "initiative": project_name or "Unknown Project",
            "metadata_uri": project_url or "https://dayof.pennapps.com/",
            "goal": 0.0
        }

# --- ORDER HISTORY ENDPOINT ---
@app.get("/orders/{user_id}")
async def get_order_history(user_id: str):
    """
    Get order history for a specific user
    """
    try:
        orders = await get_user_orders(user_id)
        
        # Convert ObjectId to string for JSON serialization
        for order in orders:
            if '_id' in order:
                order['_id'] = str(order['_id'])
            # Convert datetime objects to ISO format strings
            if 'created_at' in order and hasattr(order['created_at'], 'isoformat'):
                order['created_at'] = order['created_at'].isoformat()
        
        return JSONResponse(content={
            "success": True,
            "user_id": user_id,
            "order_count": len(orders),
            "orders": orders
        })
        
    except Exception as e:
        print(f"Error fetching order history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch order history: {str(e)}"
        )

# --- PROJECT DETAILS ENDPOINT ---
@app.get("/project/{project_id}")
async def get_project_details(project_id: str):
    """
    Fetch detailed information for a specific carbon project by ID
    """
    try:
        # Call the Carbonmark API for project details
        response = requests.get(f"https://v17.api.carbonmark.com/carbonProjects/{project_id}")
        response.raise_for_status()
        
        # Return the project data directly
        project_data = response.json()
        return JSONResponse(content=project_data)
        
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return JSONResponse(
                content={"error": f"Project with ID '{project_id}' not found"}, 
                status_code=404
            )
        else:
            return JSONResponse(
                content={"error": f"HTTP error occurred: {e.response.status_code}"}, 
                status_code=e.response.status_code
            )
    except requests.RequestException as e:
        return JSONResponse(
            content={"error": "Failed to fetch project details from Carbonmark API"}, 
            status_code=500
        )



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
