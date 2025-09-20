# CarbonChain Account System

FastAPI backend for CarbonChain user account creation with Auth0 authentication and MongoDB storage.

## Features

- ✅ User registration with Auth0 integration
- ✅ Automatic crypto wallet generation for each user
- ✅ MongoDB storage for user data
- ✅ Secure JWT token verification
- ✅ RESTful API endpoints

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. MongoDB Setup

Install and start MongoDB locally, or use MongoDB Atlas (cloud):

```bash
# Local MongoDB (Windows)
# Download from https://www.mongodb.com/try/download/community

# Or use Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 3. Auth0 Setup

1. Create an Auth0 account at https://auth0.com
2. Create a new application (Single Page Application)
3. Create an API in Auth0 dashboard
4. Note down your:
   - Domain (e.g., `your-app.auth0.com`)
   - API Audience/Identifier

### 4. Environment Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:
```
MONGODB_URL=mongodb://localhost:27017
AUTH0_DOMAIN=your-app.auth0.com
AUTH0_API_AUDIENCE=your-api-identifier
SECRET_KEY=your-random-secret-key
ENVIRONMENT=development
```

### 5. Test Setup

```bash
python test_setup.py
```

### 6. Run the API

```bash
python main.py
```

The API will be available at:
- Main API: http://127.0.0.1:8000
- API Documentation: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health

## API Endpoints

### User Management

- `POST /api/v1/users/register` - Register new user (requires Auth0 token)
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `GET /api/v1/users/wallet` - Get user's wallet address

### Authentication

All endpoints except health check require a valid Auth0 JWT token in the Authorization header:

```
Authorization: Bearer YOUR_AUTH0_JWT_TOKEN
```

## Account Creation Flow

1. User authenticates with Auth0 (frontend)
2. Frontend receives JWT token
3. Frontend calls `/api/v1/users/register` with token
4. Backend:
   - Verifies JWT token with Auth0
   - Generates new crypto wallet
   - Stores user data in MongoDB
   - Returns user profile (without private key)

## Security Notes

- Private keys are stored in the database (encrypt in production!)
- CORS is currently set to allow all origins (configure for production)
- Use HTTPS in production
- Consider using environment-specific Auth0 tenants

## Database Schema

Users collection:
```json
{
  "_id": "ObjectId",
  "email": "user@example.com",
  "auth0_id": "auth0|123456789",
  "name": "User Name",
  "wallet_address": "0x...",
  "wallet_private_key": "0x...",
  "profile_picture": "url",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```