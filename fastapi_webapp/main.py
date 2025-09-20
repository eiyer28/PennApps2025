from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Import our modules
from app.database import connect_to_mongo, close_mongo_connection
from app.users import router as users_router
from app.dev_users import router as dev_users_router

# Load environment variables
load_dotenv()

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

# Include routers
app.include_router(users_router, prefix="/api/v1", tags=["users"])
app.include_router(dev_users_router, prefix="/api/v1", tags=["development"])

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
