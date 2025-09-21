import os
import requests
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Dict, Any
import json

security = HTTPBearer()

# Auth0 configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "your-domain.auth0.com")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE", "your-api-audience")
AUTH0_ISSUER = f"https://{AUTH0_DOMAIN}/"
AUTH0_ALGORITHMS = ["RS256"]

class AuthError(Exception):
    def __init__(self, error: Dict[str, Any], status_code: int):
        self.error = error
        self.status_code = status_code

def get_token_auth_header(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Obtains the Access Token from the Authorization Header"""
    token = credentials.credentials
    return token

def verify_decode_jwt(token: str) -> Dict[str, Any]:
    """Decodes the Auth0 JWT token"""

    try:
        # Get the key from Auth0
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        print(f"Fetching JWKS from: {jwks_url}")
        jsonurl = requests.get(jwks_url)
        jwks = jsonurl.json()
        print(f"JWKS response status: {jsonurl.status_code}")

        # Get the unverified header to find the correct key
        try:
            unverified_header = jwt.get_unverified_header(token)
            print(f"Token header: {unverified_header}")
        except JWTError as e:
            print(f"JWT header error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid header. Use an RS256 signed JWT Access Token"
            )

        if unverified_header["alg"] == "HS256":
            raise HTTPException(
                status_code=401,
                detail="Invalid header. Use an RS256 signed JWT Access Token"
            )

        # Find the correct key
        rsa_key = {}
        token_kid = unverified_header["kid"]
        print(f"Looking for key ID: {token_kid}")

        for key in jwks["keys"]:
            if key["kid"] == token_kid:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                print(f"Found matching key: {key['kid']}")
                break

        if not rsa_key:
            print(f"No matching key found. Available keys: {[k['kid'] for k in jwks['keys']]}")
            raise HTTPException(
                status_code=401,
                detail="Unable to find appropriate key"
            )

        # Verify and decode the token
        try:
            print(f"Verifying token with audience: {AUTH0_API_AUDIENCE}, issuer: {AUTH0_ISSUER}")
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=AUTH0_ALGORITHMS,
                audience=AUTH0_API_AUDIENCE,
                issuer=AUTH0_ISSUER
            )
            print(f"Token verified successfully. Payload: {payload}")
            return payload
        except jwt.ExpiredSignatureError as e:
            print(f"Token expired: {e}")
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTClaimsError as e:
            print(f"JWT claims error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Incorrect claims. Please check the audience and issuer"
            )
        except Exception as e:
            print(f"Token verification error: {e}")
            raise HTTPException(
                status_code=401,
                detail=f"Unable to parse authentication token: {str(e)}"
            )

    except Exception as e:
        print(f"General auth error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )

async def get_current_user(token: str = Security(get_token_auth_header)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    try:
        payload = verify_decode_jwt(token)
        return payload
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not validate credentials")