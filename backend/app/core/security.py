"""Authentication and authorization utilities."""

from datetime import datetime, timedelta
from typing import Optional, Dict

import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext


# Simple in-memory stores (replace with PostgreSQL repositories in production)
USERS_DB = {}
PROJECTS_DB = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def check_permission(user_role: str, required_role: str) -> bool:
    role_hierarchy = {"developer": 1, "team_lead": 2}
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
