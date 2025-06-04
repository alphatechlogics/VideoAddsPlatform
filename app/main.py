from fastapi import FastAPI, Depends
from app.api.routes import router as api_router
from app.api.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.auth import verify_api_key
from app.config.settings import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.is_production else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Video Ads Platform API",
    description="Secure API for video and ad search",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth routes without token verification
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

# API routes with token verification
app.include_router(
    api_router, 
    prefix="/api", 
    # dependencies=[Depends(verify_api_key)],
    tags=["api"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
