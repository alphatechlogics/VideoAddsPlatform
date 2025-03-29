from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from app.config.settings import settings
from app.models.auth import UserInDB, TokenData
from app.config.settings import settings
from fastapi import HTTPException, status
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This is a mock user database - replace with your actual database
MOCK_DB = {
    "testuser": {
        "username": settings.username,
        "email": settings.email,
        "hashed_password": pwd_context.hash(settings.password),
        "disabled": False
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[UserInDB]:
    if username in MOCK_DB:
        user_dict = MOCK_DB[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret_key, 
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt
