from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class VideoBase(BaseModel):
    title: str
    description: Optional[str]
    video_id: str
    channel_id: str
    url: str
    
class VideoMetadata(BaseModel):
    views: int
    likes: int
    comments: int
    upload_date: datetime


class Video(VideoBase):
    metadata: VideoMetadata
