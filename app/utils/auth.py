from jose import jwt
from datetime import datetime, timedelta
from app.config.settings import settings

def create_access_token() -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    encoded_jwt = jwt.encode(
        {"exp": expire}, 
        settings.JWT_SECRET_KEY,
        algorithms=settings.jwt_algorithm
    )
    return encoded_jwt
