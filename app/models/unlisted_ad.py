from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime

class VideoCategory(str, Enum):
    AUTOS_VEHICLES = "Autos & Vehicles"       # 12
    COMEDY = "Comedy"                         # 30
    EDUCATION = "Education"                   # 33
    ENTERTAINMENT = "Entertainment"           # 8
    FILM_ANIMATION = "Film & Animation"       # 18
    GAMING = "Gaming"                         # 9
    HOWTO_STYLE = "Howto & Style"            # 6
    MOVIES = "Movies"                         # 42
    MUSIC = "Music"                          # 14
    NOT_AVAILABLE = "N/A"                    # 0
    NEWS_POLITICS = "News & Politics"         # 46
    NONPROFITS_ACTIVISM = "Nonprofits & Activism" # 2
    PEOPLE_BLOGS = "People & Blogs"          # 35
    PETS_ANIMALS = "Pets & Animals"          # 39
    SCIENCE_TECH = "Science & Technology"    # 3
    SHORTS = "Shorts"                        # 49
    SHOWS = "Shows"                          # 32
    SPORTS = "Sports"                        # 7
    TRAILERS = "Trailers"                    # 26
    TRAVEL_EVENTS = "Travel & Events"        # 19

class LanguageInfo(BaseModel):
    auto_generated: List[str] = Field(default_factory=list)
    subtitles: List[str] = Field(default_factory=list)

class ChannelInfo(BaseModel):
    name: str
    channel_id: str
    subscribers: str

class UnlistedVideo(BaseModel):
    title: str
    video_id: str
    url: str
    thumbnail: str
    channel_name: str
    channel_id: str
    subscribers: str
    category: VideoCategory
    duration: str
    duration_seconds: int
    views: str
    likes: str
    dislikes: str
    upload_date: str
    languages: LanguageInfo
    channel_info: Optional[ChannelInfo] = None

    class Config:
        use_enum_values = True
