from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
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
        self.youtube = build("youtube", "v3", developerKey=settings.youtube_api_key)

    async def search_video_ads(self, keyword: str = None, category: str = None) -> List[Ad]:
        """Search for video advertisements on YouTube"""
        try:
            search_params = {
                'q': f"{keyword} advertisement" if keyword else "advertisement",
                'part': "snippet",
                'type': "video",
                'maxResults': 50,
                'videoDuration': "short",  # Most ads are short
                'relevanceLanguage': 'en'
            }

            if category:
                search_params['q'] = f"{category} {search_params['q']}"
            
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
                        category="video"
                    )
                    ads.append(ad)
                except Exception as e:
                    logger.error(f"Error processing ad: {str(e)}")
                    continue

            logger.info(f"Found {len(ads)} video ads")
            return ads

        except Exception as e:
            logger.error(f"Error searching video ads: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))