from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    youtube_api_key: str 
    rate_limit_per_minute: int = 60
    environment: str = "development"
    JWT_SECRET_KEY: str 
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120

    @property
    def is_production(self):
        return self.environment == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
