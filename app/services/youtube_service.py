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

logger = logging.getLogger(__name__)

class YouTubeService:
    def __init__(self):
        try:
            self.youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)
            logger.info("YouTube service initialized successfully") 
        except Exception as e:
            logger.error(f"Failed to initialize YouTube service: {str(e)}")
            raise

    async def search_videos(self, keyword: str = None, category: str = None, channel_name: str = None) -> List[Video]:
        try:
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
            logger.error(f"Error searching videos: {str(e)}")
            raise Exception(f"Error searching videos: {str(e)}")

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
