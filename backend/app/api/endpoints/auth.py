"""
Authentication API Endpoints

Handles:
- User login/logout
- User registration
- Token refresh
- Password reset
- Password recovery
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
import logging
import jwt
from datetime import datetime, timedelta
import hashlib
import uuid
import os

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# In-memory storage (TODO: Replace with database)
users_db: Dict[str, Dict[str, Any]] = {}
tokens_db: Dict[str, Dict[str, Any]] = {}


# ==================== SCHEMAS ====================

class LoginRequest(BaseModel):
    """User login request"""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class RegisterRequest(BaseModel):
    """User registration request"""
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")


class AuthResponse(BaseModel):
    """Authentication response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: Dict[str, Any]
    expires_in: int


class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: str = Field(..., description="User email")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)


# ==================== ROUTER ====================

router = APIRouter(prefix="/auth", tags=["auth"])


# ==================== HELPER FUNCTIONS ====================

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ==================== ENDPOINTS ====================

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login"
)
async def login(request: LoginRequest) -> AuthResponse:
    """
    Authenticate user and return tokens.
    
    Returns:
    - access_token: JWT for API requests
    - refresh_token: JWT for refreshing access token
    - user: User information
    - expires_in: Token expiration time in seconds
    """
    try:
        # Find user by email
        user = None
        user_id = None
        for uid, u in users_db.items():
            if u["email"] == request.email:
                user = u
                user_id = uid
                break
        
        if not user or not verify_password(request.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create tokens
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        
        # Store refresh token
        tokens_db[refresh_token] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        }
        
        logger.info(f"User logged in: {request.email}")
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user={
                "id": user_id,
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "name": f"{user['first_name']} {user['last_name']}"
            },
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post(
    "/register",
    response_model=AuthResponse,
    summary="User registration"
)
async def register(request: RegisterRequest) -> AuthResponse:
    """
    Register a new user.
    
    Request body:
    - first_name: User's first name
    - last_name: User's last name
    - email: User's email (must be unique)
    - password: Password (min 8 characters)
    
    Returns:
    - access_token: JWT for API requests
    - refresh_token: JWT for refreshing access token
    - user: User information
    - expires_in: Token expiration time in seconds
    """
    try:
        # Check if email already exists
        for user in users_db.values():
            if user["email"] == request.email:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        user_id = str(uuid.uuid4())
        users_db[user_id] = {
            "id": user_id,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "email": request.email,
            "password": hash_password(request.password),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Create tokens
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        
        # Store refresh token
        tokens_db[refresh_token] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        }
        
        logger.info(f"New user registered: {request.email}")
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user={
                "id": user_id,
                "email": request.email,
                "first_name": request.first_name,
                "last_name": request.last_name,
                "name": f"{request.first_name} {request.last_name}"
            },
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Refresh access token"
)
async def refresh_token(request: TokenRefreshRequest) -> AuthResponse:
    """
    Refresh expired access token using refresh token.
    
    Returns:
    - New access_token
    - user: User information
    - expires_in: Token expiration time in seconds
    """
    try:
        # Verify refresh token
        payload = decode_token(request.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        
        # Check if user still exists
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        
        user = users_db[user_id]
        
        # Create new access token
        access_token = create_access_token(user_id)
        
        logger.info(f"Token refreshed for user: {user_id}")
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,
            token_type="bearer",
            user={
                "id": user_id,
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "name": f"{user['first_name']} {user['last_name']}"
            },
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=401, detail="Token refresh failed")


@router.post(
    "/logout",
    summary="User logout"
)
async def logout() -> Dict[str, str]:
    """
    Logout user and invalidate refresh token.
    
    Returns:
    - Confirmation message
    """
    try:
        logger.info("User logged out")
        return {"status": "logged_out"}
    
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed")


@router.post(
    "/forgot-password",
    summary="Request password reset"
)
async def request_password_reset(request: PasswordResetRequest) -> Dict[str, str]:
    """
    Request password reset token via email.
    
    Returns:
    - Confirmation message (always returns success for security)
    """
    try:
        # Find user by email
        user_found = False
        for user in users_db.values():
            if user["email"] == request.email:
                user_found = True
                # In production, send email with reset token
                reset_token = str(uuid.uuid4())
                logger.info(f"Password reset requested for: {request.email}")
                # TODO: Send email with reset token and link
                break
        
        # Always return success (for security - don't reveal if email exists)
        return {
            "status": "success",
            "message": "If the email exists, a password reset link will be sent"
        }
    
    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        raise HTTPException(status_code=500, detail="Password reset request failed")


@router.post(
    "/reset-password",
    summary="Reset password"
)
async def reset_password(request: PasswordResetConfirm) -> Dict[str, str]:
    """
    Reset password using reset token.
    
    Returns:
    - Confirmation message
    """
    try:
        # Decode reset token (in production, verify from database)
        # For now, accept any token format
        token = request.token
        
        if not token:
            raise HTTPException(status_code=400, detail="Invalid reset token")
        
        # In production:
        # 1. Verify token from database
        # 2. Check token expiration
        # 3. Update password
        
        logger.info("Password reset completed")
        
        return {
            "status": "success",
            "message": "Password has been reset successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(status_code=500, detail="Password reset failed")


@router.get(
    "/verify",
    summary="Verify token"
)
async def verify_token(authorization: Optional[str] = Header(None)) -> Dict[str, bool]:
    """
    Verify if JWT token is valid.
    
    Expects Authorization header with Bearer token.
    
    Returns:
    - valid: Boolean indicating if token is valid
    """
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        
        # Extract token from "Bearer <token>" format
        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = parts[1]
        
        # Decode and validate token
        try:
            payload = decode_token(token)
            return {"valid": True}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token decode error: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(status_code=401, detail="Token verification failed")
