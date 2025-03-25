from googleapiclient.discovery import build
from app.config.settings import settings
from app.models.video import Video, VideoMetadata
from typing import List
from datetime import datetime

class YouTubeService:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)

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
            if category:
                search_params['videoCategoryId'] = category

            request = self.youtube.search().list(**search_params)
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                metadata = await self.get_video_metadata(video_id)
                
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
            
            return videos
            
        except Exception as e:
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
            raise Exception(f"Error fetching video metadata: {str(e)}")
