from calendar import c
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from app.config.settings import settings
from app.models.video import Video, VideoMetadata
from typing import List, Optional, Dict
from datetime import datetime
import logging
import json
import os
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class YouTubeService:
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

    async def search_videos(self, keyword: str = None, category: str = None, channel_name: str = None) -> List[Video]:
        try:
            # Input validation
            if not any([keyword, category, channel_name]):
                raise HTTPException(status_code=400, detail="At least one search parameter is required")
            
            search_params = {
                'part': 'snippet',
                'maxResults': 50,
                'type': 'video'
            }
            
            if keyword:
                search_params['q'] = keyword
            if category:
                search_params['q'] = category
            if channel_name:
                search_params['q'] = channel_name

            logger.debug(f"Searching videos with params: {search_params}")
            request = self.youtube.search().list(**search_params)
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                metadata = await self.get_video_metadata(video_id)
                    
                # Create video object
                try:
                    video = Video(
                        title=item['snippet']['title'],
                        description=item['snippet']['description'],
                        video_id=video_id,
                        channel_id=item['snippet']['channelId'],
                        url=f"https://www.youtube.com/watch?v={video_id}",
                        metadata=VideoMetadata(
                            views=int(metadata['statistics'].get('viewCount', 0)),
                            likes=int(metadata['statistics'].get('likeCount', 0)),
                            comments=int(metadata['statistics'].get('commentCount', 0)),
                            upload_date=datetime.strptime(
                                item['snippet']['publishedAt'],
                                '%Y-%m-%dT%H:%M:%SZ'
                            ),
                                  
                        )
                    )
                    videos.append(video)
                except Exception as e:
                    logger.error(f"Error processing video {video_id}: {str(e)}")
                    continue
            
            logger.info(f"Found {len(videos)} videos matching criteria")
            return videos
            
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg:
                raise HTTPException(status_code=429, detail="YouTube API quota exceeded")
            elif "invalid" in error_msg:
                raise HTTPException(status_code=400, detail="Invalid search parameters")
            else:
                logger.error(f"Error searching videos: {str(e)}")
                raise HTTPException(status_code=500, detail="Error searching videos")

    async def get_video_metadata(self, video_id: str) -> dict:
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()
            if response['items']:
                return response['items'][0]
            return {}
        except Exception as e:
            logger.error(f"Error fetching video metadata: {str(e)}")
            raise Exception(f"Error fetching video metadata: {str(e)}")
