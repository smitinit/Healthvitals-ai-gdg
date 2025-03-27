import os
from functools import wraps
from flask import request, jsonify
try:
    from jose import jwt
    from jose.exceptions import JWTError
except ImportError:
    # Fallback to PyJWT if python-jose is not available
    import jwt
    from jwt import PyJWTError as JWTError
import requests
import logging
from clerk_backend_api import Clerk
import base64

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize Clerk client with API key from environment
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", "https://present-tiger-42.clerk.accounts.dev/.well-known/jwks.json")
CLERK_ISSUER = os.getenv("CLERK_ISSUER", "https://present-tiger-42.clerk.accounts.dev")

# Initialize Clerk client if secret key is available
clerk = None
if CLERK_SECRET_KEY:
    clerk = Clerk(bearer_auth=CLERK_SECRET_KEY)

# Cache JWKS for better performance
_jwks_cache = None

def get_jwks():
    """Fetch and cache JSON Web Key Set from Clerk"""
    global _jwks_cache
    if _jwks_cache is None:
        try:
            response = requests.get(CLERK_JWKS_URL)
            response.raise_for_status()
            _jwks_cache = response.json()
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {str(e)}")
            _jwks_cache = {"keys": []}
    return _jwks_cache

def verify_token(token):
    """Verify a JWT token using JWKS keys from Clerk"""
    try:
        # Get token headers without verification
        try:
            # python-jose way
            headers = jwt.get_unverified_headers(token)
        except AttributeError:
            # PyJWT way
            headers = jwt.get_unverified_header(token)
            
        kid = headers.get('kid')
        
        if not kid:
            logger.error("No 'kid' in token headers")
            return None
        
        # Find the matching key
        jwks = get_jwks()
        key = None
        for k in jwks.get('keys', []):
            if k.get('kid') == kid:
                key = k
                break
        
        if not key:
            logger.error(f"No key found for kid: {kid}")
            return None
        
        # Convert JWKS key to PEM format
        try:
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import serialization
            
            # Extract the modulus and exponent from the JWKS key
            n = int.from_bytes(base64.urlsafe_b64decode(key['n'] + '=' * (4 - len(key['n']) % 4)), byteorder='big')
            e = int.from_bytes(base64.urlsafe_b64decode(key['e'] + '=' * (4 - len(key['e']) % 4)), byteorder='big')
            
            # Create RSA public key
            public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())
            
            # Export as PEM
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Verify and decode the token
            payload = jwt.decode(
                token,
                pem,
                algorithms=['RS256'],
                audience='https://healthvitals-ai.com',
                issuer=CLERK_ISSUER,
                options={"verify_aud": False}
            )
            
            return payload
            
        except Exception as e:
            logger.error(f"Error converting JWKS to PEM: {str(e)}")
            return None
            
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        return None

def get_token_from_header():
    """Extract token from Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    return auth_header.split(' ')[1]

def require_auth(f):
    """Decorator to require authentication on routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({"error": "Authorization token required"}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Add user information to the request context
        request.user_id = payload.get('sub')
        request.user_info = payload
        
        return f(*args, **kwargs)
    return decorated

def optional_auth(f):
    """Decorator to optionally use authentication if provided"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if token:
            payload = verify_token(token)
            if payload:
                request.user_id = payload.get('sub')
                request.user_info = payload
            else:
                request.user_id = None
                request.user_info = None
        else:
            request.user_id = None
            request.user_info = None
        
        return f(*args, **kwargs)
    return decorated

def is_authenticated():
    """Check if the current request is authenticated"""
    token = get_token_from_header()
    if not token:
        return False
    
    payload = verify_token(token)
    if not payload:
        return False
    
    return True

def get_current_user_id():
    """Get the current user ID from the authenticated request"""
    token = get_token_from_header()
    if not token:
        return None
    
    payload = verify_token(token)
    if not payload:
        return None
    
    return payload.get('sub') 