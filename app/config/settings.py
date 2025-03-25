from pydantic_settings import BaseSettings
from pydantic import validator
from typing import Optional

class Settings(BaseSettings):
    youtube_api_key: str
    google_ads_developer_token: str
    google_ads_client_id: str
    google_ads_client_secret: str
    google_ads_refresh_token: str
    google_ads_login_customer_id: str
    google_ads_use_proto_plus: bool = True

    @validator('google_ads_developer_token')
    def clean_developer_token(cls, v):
        # Remove 'Bearer ' prefix if present
        if v.startswith('Bearer '):
            v = v[7:]
        return v.strip()

    @validator('google_ads_login_customer_id')
    def clean_customer_id(cls, v):
        # Remove any dashes and non-numeric characters
        return ''.join(filter(str.isdigit, str(v)))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
