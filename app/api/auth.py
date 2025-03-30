from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.models.auth import Token
from app.config.settings import settings
from datetime import datetime, timedelta
from jose import jwt
import logging
import secrets

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

@router.post("/token", response_model=Token)
async def get_access_token():
    """Generate access token without authentication"""
    try:
        # Generate token with expiration
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        token_data = {
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": secrets.token_hex(16)  # Add unique token ID
        }
        
        access_token = jwt.encode(
            token_data,
            str(settings.JWT_SECRET_KEY),
            algorithm=settings.jwt_algorithm
        )
        
        logger.info("Successfully generated access token")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_expire_minutes * 60
        }
    except Exception as e:
        logger.error(f"Failed to generate token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating access token: {str(e)}"
        )
