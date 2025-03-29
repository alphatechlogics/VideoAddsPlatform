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


@router.get("/search-videos", response_model=List[Video])
async def search_videos(
    youtube_service: YouTubeService = Depends(),
    keyword: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    channel_name: Optional[str] = Query(None)
):
    return await youtube_service.search_videos(keyword, category, channel_name)

@router.get("/search-video-ads", response_model=List[Ad])
async def search_video_ads(
    ads_service: GoogleAdsService = Depends(),
    keyword: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    channel_name: Optional[str] = Query(None)
):
    return await ads_service.search_video_ads(keyword, category, channel_name)
