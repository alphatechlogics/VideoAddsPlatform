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
            # Load credentials from token.json
            if os.path.exists('token.json'):
                with open('token.json') as token:
                    creds_data = json.load(token)
                    creds = Credentials.from_authorized_user_info(creds_data)
            else:
                creds = None

            if not creds or not creds.valid:
                raise Exception("No valid credentials found. Please run token_creator.py first.")

            self.youtube = build('youtube', 'v3', credentials=creds)
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
            
            for item in response.get('items', []):
                category_id = item['id']
                category_name = item['snippet']['title'].lower()
                self.category_mapping[category_name] = category_id
                
            logger.info(f"Loaded {len(self.category_mapping)} video categories")
        except Exception as e:
            logger.error(f"Error loading video categories: {str(e)}")
            # Fallback to basic categories if API call fails
            self.category_mapping = {
                'music': '10',
                'entertainment': '24',
                'gaming': '20',
                'sports': '17',
                'news': '25',
                'education': '27',
                'science': '28',
                'technology': '28',
                'travel': '19',
                'howto': '26'
            }

    async def search_videos(self, keyword: str = None, category: str = None, channel_id: str = None) -> List[Video]:
        try:
            search_params = {
                'part': 'snippet',
                'maxResults': 50,
                'type': 'video'
            }
            
            if keyword:
                search_params['q'] = keyword
            if channel_id:
                search_params['channelId'] = channel_id

            logger.debug(f"Searching videos with params: {search_params}")
            request = self.youtube.search().list(**search_params)
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                metadata = await self.get_video_metadata(video_id)
                
                # Filter by category if specified
                if category:
                    category_id = self.category_mapping.get(category.lower())
                    if category_id and metadata['snippet'].get('categoryId') != category_id:
                        continue

                video = Video(
                    title=item['snippet']['title'],
                    description=item['snippet']['description'],
                    video_id=video_id,
                    channel_id=item['snippet']['channelId'],
                    metadata=VideoMetadata(
                        views=int(metadata['statistics'].get('viewCount', 0)),
                        likes=int(metadata['statistics'].get('likeCount', 0)),
                        comments=int(metadata['statistics'].get('commentCount', 0)),
                        upload_date=datetime.strptime(
                            item['snippet']['publishedAt'],
                            '%Y-%m-%dT%H:%M:%SZ'
                        ),
                        categories=[metadata['snippet'].get('categoryId', 'undefined')]
                    )
                )
                videos.append(video)
            
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
