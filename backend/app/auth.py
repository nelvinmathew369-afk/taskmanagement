import hashlib
import os
import datetime
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash password securely using PBKDF2 with SHA-256 and salt."""
    salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()
    return f"{salt}${hashed}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify a plain password against the stored salt$hash."""
    try:
        salt, expected_hash = stored_hash.split("$", 1)
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        ).hex()
        return actual_hash == expected_hash
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Create a signed JWT token."""
    to_encode = data.copy()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Retrieve current authenticated user if token is present, else None."""
    if not credentials:
        return None
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return db.query(User).filter(User.username == username).first()
    except (jwt.PyJWTError, Exception):
        return None


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Enforce authentication requirement for protected endpoints."""
    user = get_current_user_optional(credentials, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def seed_demo_user_if_needed(db: Session):
    """Seed default demo user for easy walkthrough/demonstration."""
    demo_user = db.query(User).filter(User.username == "admin").first()
    if not demo_user:
        new_user = User(
            username="admin",
            email="admin@company.com",
            password_hash=hash_password("admin123"),
            full_name="Assessment Evaluator",
        )
        db.add(new_user)
        db.commit()
