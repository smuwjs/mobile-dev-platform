"""Auth API endpoints."""
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

# In-memory user storage
_users_db: dict = {}

JWT_SECRET = "dev-secret-key"
JWT_ALGORITHM = "HS256"


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


def create_token(user_id: str, token_type: str = "access") -> str:
    """Create JWT token."""
    if token_type == "access":
        exp = datetime.utcnow() + timedelta(minutes=30)
    else:
        exp = datetime.utcnow() + timedelta(days=7)
    payload = {
        "sub": user_id,
        "exp": exp,
        "iat": datetime.utcnow(),
        "type": token_type,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register", status_code=201)
def register(user: UserCreate):
    """Register a new user."""
    if user.username in _users_db:
        raise HTTPException(status_code=400, detail="Username already exists")

    user_id = secrets.token_urlsafe(8)
    _users_db[user.username] = {
        "id": user_id,
        "username": user.username,
        "password": user.password,
        "email": user.email,
        "created_at": datetime.utcnow().isoformat(),
    }
    return {"message": "User registered", "user_id": user_id}


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    """Login and get token."""
    user = _users_db.get(credentials.username)
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user["id"])
    return TokenResponse(access_token=token)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshRequest):
    """Refresh access token."""
    payload = verify_token(request.refresh_token)
    token_type = payload.get("type", "access")

    # Only refresh tokens can be used to get new access tokens
    if token_type != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type for refresh")

    user_id = payload.get("sub")
    new_token = create_token(user_id, token_type="access")
    return TokenResponse(access_token=new_token)


@router.get("/me")
def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user info."""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")

    for user in _users_db.values():
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user.get("email"),
            }
    raise HTTPException(status_code=404, detail="User not found")