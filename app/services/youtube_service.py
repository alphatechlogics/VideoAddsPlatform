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
            self.category_mapping = {}
            self._load_categories()
            logger.info("YouTube service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube service: {str(e)}")
            raise

    def _load_categories(self):
        try:
            request = self.youtube.videoCategories().list(
                part="snippet",
                regionCode="US"
            )
            response = request.execute()
            
            # Add both ID->name and name->ID mappings
            self.category_mapping = {}
            for item in response.get('items', []):
                category_name = item['snippet']['title'].lower()
                category_id = item['id']
                self.category_mapping[category_name] = category_id
                self.category_mapping[category_id] = category_name
            
            logger.debug(f"Loaded categories: {self.category_mapping}")
            logger.info(f"Loaded {len(self.category_mapping) // 2} video categories")
        except Exception as e:
            logger.error(f"Error loading video categories: {str(e)}")
            # Fallback categories if API fails
            self.category_mapping = {
                'entertainment': '24', '24': 'entertainment',
                'music': '10', '10': 'music',
                'gaming': '20', '20': 'gaming',
                'sports': '17', '17': 'sports',
                'news': '25', '25': 'news'
            }

    async def get_channel_id_by_name(self, channel_name: str) -> Optional[str]:
        try:
            request = self.youtube.search().list(
                part="snippet",
                type="channel",
                q=channel_name,
                maxResults=1
            )
            response = request.execute()

            if response.get('items'):
                return response['items'][0]['id']['channelId']
            return None
        except Exception as e:
            logger.error(f"Error finding channel ID: {str(e)}")
            return None

    async def search_videos(self, keyword: str = None, category: str = None, channel_name: str = None) -> List[Video]:
        try:
            search_params = {
                'part': 'snippet',
                'maxResults': 50,
                'type': 'video'
            }
            
            if keyword:
                search_params['q'] = keyword

            # Convert channel name to channel ID if provided
            if channel_name:
                channel_id = await self.get_channel_id_by_name(channel_name)
                if channel_id:
                    search_params['channelId'] = channel_id
                else:
                    logger.warning(f"Channel not found: {channel_name}")
                    return []

            logger.debug(f"Searching videos with params: {search_params}")
            request = self.youtube.search().list(**search_params)
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                metadata = await self.get_video_metadata(video_id)
                
                # Filter by category if specified
                if category and metadata.get('snippet'):
                    video_category_id = metadata['snippet'].get('categoryId')
                    video_category_name = self.category_mapping.get(video_category_id, '').lower()
                    if category.lower() not in [video_category_id, video_category_name]:
                        continue

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
                            categories=[self.category_mapping.get(metadata['snippet'].get('categoryId'), 'undefined')]            
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
