"""Auth service for user management and JWT handling."""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import settings

# In-memory user storage
_users_db: dict[str, dict] = {}

# Token blacklist (for future use with refresh tokens)
_token_blacklist: set[str] = set()


def _hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(
    email: str,
    username: str,
    password: str,
    full_name: str | None = None,
) -> dict:
    """Create a new user in memory storage."""
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    user = {
        "id": user_id,
        "email": email,
        "username": username,
        "hashed_password": _hash_password(password),
        "full_name": full_name,
        "avatar_url": None,
        "is_active": True,
        "is_superuser": False,
        "last_login_at": None,
        "created_at": now,
        "updated_at": now,
    }

    _users_db[user_id] = user
    _users_db[f"email:{email}"] = user
    _users_db[f"username:{username}"] = user

    return user


def get_user_by_id(user_id: str) -> dict | None:
    """Get user by ID."""
    return _users_db.get(user_id)


def get_user_by_email(email: str) -> dict | None:
    """Get user by email."""
    return _users_db.get(f"email:{email}")


def get_user_by_username(username: str) -> dict | None:
    """Get user by username."""
    return _users_db.get(f"username:{username}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return _hash_password(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt.access_token_expire_minutes
        )

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm,
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt.secret_key,
            algorithms=[settings.jwt.algorithm],
        )
        return payload
    except JWTError:
        return None


def blacklist_token(jti: str) -> None:
    """Add a token to the blacklist."""
    _token_blacklist.add(jti)


def is_token_blacklisted(jti: str) -> bool:
    """Check if a token is blacklisted."""
    return jti in _token_blacklist
