from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from app.services.youtube_service import YouTubeService
from app.services.ads_service import GoogleAdsService
from app.models.video import Video
from app.models.ad import Ad
# from pydantic import BaseModel
import os
from dotenv import load_dotenv

router = APIRouter()
load_dotenv()

@router.get("/")
async def root():
    return {"message": "Video Ads API is running"}

@router.get("/youtube/status")
async def youtube_status():
    api_key = os.getenv("YOUTUBE_API_KEY")
    return {"status": "connected" if api_key else "not configured"}

@router.get("/ads/status")
async def ads_status():
    developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
    return {"status": "connected" if developer_token else "not configured"}

@router.get("/search-videos", response_model=List[Video])
async def search_videos(
    youtube_service: YouTubeService = Depends(),
    keyword: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    channel_id: Optional[str] = Query(None)
):
    return await youtube_service.search_videos(keyword, category, channel_id)

@router.get("/search-ads", response_model=List[Ad])
async def search_ads(
    ads_service: GoogleAdsService = Depends(),
    keyword: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    return await ads_service.search_ads(keyword, category)
