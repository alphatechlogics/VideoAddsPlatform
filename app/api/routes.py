from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional, Dict, Union
from app.services.youtube_service import YouTubeService
from app.services.ads_service import GoogleAdsService
from app.services.unlisted_ads import UnlistedVideoFinder
from app.models.video import Video
from app.models.ad import Ad
from app.models.unlisted_ad import UnlistedVideo, VideoCategory
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

router = APIRouter()
load_dotenv()

unlisted_finder = UnlistedVideoFinder()

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

@router.get("/categories")
async def get_available_categories():
    """Get list of available video categories."""
    return {
        "categories": [cat.value for cat in VideoCategory],
        "total": len(VideoCategory)
    }

@router.get("/search-unlisted", response_model=Dict[str, Union[int, List[UnlistedVideo]]])
async def search_unlisted_videos(
    keyword: Optional[str] = Query(None, description="Search term"),
    category: Optional[VideoCategory] = Query(None, description="Video category"),
    channel_id: Optional[str] = Query(None, description="Channel ID"),
    ads_only: bool = Query(True, description="Only return short videos suitable for ads")
):
    """
    Search for unlisted videos with various filters.
    Returns videos sorted by view count.
    """
    try:
        videos = await unlisted_finder.search_unlisted_videos(
            keyword=keyword,
            category=category.value if category else None,
            channel_id=channel_id,
            ads_only=ads_only
        )
        
        # Convert dictionary results to UnlistedVideo models
        video_models = [UnlistedVideo(**video) for video in videos]
        return {"count": len(video_models), "videos": video_models}
        
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"detail": str(e)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
