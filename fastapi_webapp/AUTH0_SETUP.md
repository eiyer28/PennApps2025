# Auth0 Setup Guide for CarbonChain

## Development Mode (Current)
✅ **Your system is working in development mode!**

**Available endpoints (no Auth0 required):**
- `POST /api/v1/dev/users/register` - Register user
- `GET /api/v1/dev/users/me` - Get user profile
- `GET /api/v1/dev/users/wallet` - Get wallet address
- `GET /api/v1/dev/status` - Check dev mode status

**Example registration:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/dev/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "auth0_id": "dev_test_123", "name": "Test User"}'
```

---

## Setting up Auth0 (Optional - for production)

### Step 1: Create Auth0 Account
1. Go to https://auth0.com
2. Sign up for free account
3. Create a new tenant (e.g., "carbonchain-dev")

### Step 2: Create Application
1. Go to Applications > Create Application
2. Choose "Single Page Application"
3. Name it "CarbonChain Frontend"
4. Note the **Domain** and **Client ID**

### Step 3: Create API
1. Go to Applications > APIs > Create API
2. Name: "CarbonChain API"
3. Identifier: "carbonchain-api" (this is your audience)
4. Note the **Identifier/Audience**

### Step 4: Update Environment
Update your `.env` file:
```env
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_API_AUDIENCE=carbonchain-api
DEV_MODE=false  # To disable dev endpoints
```

### Step 5: Test Auth0
1. Go to Applications > APIs > CarbonChain API > Test
2. Copy the test token
3. Use it in curl:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/users/register \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "auth0_id": "auth0|123", "name": "Test User"}'
```

---

## Switching Between Modes

**Development Mode** (current):
- `DEV_MODE=true` in `.env`
- Use `/api/v1/dev/*` endpoints
- No Auth0 tokens required

**Production Mode**:
- `DEV_MODE=false` in `.env`
- Use `/api/v1/users/*` endpoints
- Requires Auth0 JWT tokens

---

## API Documentation
Visit http://127.0.0.1:8000/docs to see all available endpoints in Swagger UI.