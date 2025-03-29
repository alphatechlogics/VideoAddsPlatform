from fastapi import HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader
from app.config.settings import settings
from datetime import datetime, timedelta
from jose import jwt, JWTError
import logging

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)  # Changed to False to handle manually

class RateLimiter:
    def __init__(self):
        self.requests = {}  # {client_id: [timestamps]}
        self.limit = settings.rate_limit_per_minute
        
    def is_rate_limited(self, client_id: str) -> bool:
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        if client_id not in self.requests:
            return False
            
        # Filter requests within the last minute
        recent_requests = [
            timestamp for timestamp in self.requests[client_id] 
            if timestamp > minute_ago
        ]
        
        # Update requests with only recent ones
        self.requests[client_id] = recent_requests
        
        # Check if number of recent requests exceeds limit
        return len(recent_requests) >= self.limit

    def add_request(self, client_id: str):
        if client_id not in self.requests:
            self.requests[client_id] = []
        self.requests[client_id].append(datetime.now())

rate_limiter = RateLimiter()

async def verify_api_key(request: Request, api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="No token provided. Please include X-API-Key header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Verify the token is valid JWT
        payload = jwt.decode(
            api_key,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.jwt_algorithm]
        )
        
        # Check if token is expired
        if 'exp' in payload:
            exp_timestamp = payload['exp']
            if datetime.utcnow().timestamp() > exp_timestamp:
                raise HTTPException(
                    status_code=401,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
    except JWTError as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token format or signature",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Rate limiting check
    client_id = request.client.host
    if rate_limiter.is_rate_limited(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    rate_limiter.add_request(client_id)
    return api_key
