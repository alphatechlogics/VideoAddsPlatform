from app.config.settings import settings
from app.models.ad import Ad
from typing import List
from fastapi import HTTPException
import logging
from googleapiclient.discovery import build


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GoogleAdsService:
    def __init__(self):
        try:
            if not settings.youtube_api_key:
                raise ValueError("YouTube API key is not configured")
            self.youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)
            logger.info("YouTube service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube service: {str(e)}")
            if "quota" in str(e).lower():
                raise HTTPException(status_code=429, detail="YouTube API quota exceeded")
            elif "invalid" in str(e).lower():
                raise HTTPException(status_code=401, detail="Invalid YouTube API key")
            else:
                raise HTTPException(status_code=500, detail="YouTube service initialization failed")


    async def search_video_ads(self, keyword: str = None, category: str = None, channel_name: str = None) -> List[Ad]:
        """Search for video advertisements on YouTube"""
        try:
            search_params = {
                'q': f"{keyword} advertisement" if keyword else "advertisement",
                'part': "snippet",
                'type': "video",
                'maxResults': 50,
                'videoDuration': "short"  # Most ads are short
            }

            if category:
                search_params['q'] = f"{category} advertisement" if category else "advertisement"

            if channel_name:
                search_params['q'] = channel_name
                    
            logger.debug(f"Searching YouTube ads with params: {search_params}")
            response = self.youtube.search().list(**search_params).execute()

            ads = []
            for item in response.get("items", []):
                try:
                    ad = Ad(
                        ad_id=item["id"]["videoId"],
                        advertiser=item["snippet"]["channelTitle"],
                        duration=0,  # Duration could be fetched with additional API call
                        metadata={
                            "title": item["snippet"]["title"],
                            "description": item["snippet"]["description"],
                            "publishedAt": item["snippet"]["publishedAt"],
                            "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
                            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                        },
                        
                    )
                    ads.append(ad)
                except Exception as e:
                    return (f"Error processing ad: {str(e)}")
                    continue

            logger.info(f"Found {len(ads)} video ads")
            return ads

        except Exception as e:
            logger.error(f"Error searching video ads: {str(e)}")
            raise HTTPException(status_code=500, detail={str(e)})