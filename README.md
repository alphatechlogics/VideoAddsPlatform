# Video Ads Platform API

A FastAPI-based platform that integrates YouTube and Google Ads APIs to search for videos and video advertisements.

## Features

- YouTube video search with filters for:
  - Keywords
  - Categories
  - Channel names
- Video advertisement search with:
  - Keyword filtering
  - Category filtering
  - Channel name filtering
  - Duration-based filtering
- RESTful API endpoints
- Swagger/OpenAPI documentation
- Error handling and logging

## Quick Start

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment Variables**
Create a `.env` file with:
```env
YOUTUBE_API_KEY=your_youtube_api_key
JWT_SECRET_KEY=your_jwt_secret_key
```

3. **Run the Application**
```bash
./run.sh
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Access API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register`
  - Request body: username, email, password
  - Returns: user details
  - Description: Register a new user
  
- `POST /api/auth/token`
-  Request body: username, password (form-data)
  - Returns: JWT token
  - Description: Generate a token for authentication

### Videos
- `GET /api/search-videos`
  - Query params: keyword, category, channel_name
  - Returns list of videos with metadata

### Advertisements
- `GET /api/search-video-ads`
  - Query params: keyword, category
  - Returns list of video advertisements


## Project Structure
```
video and ads/
├── app/
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   └── auth.py            # Authentication endpoints
│   ├── config/
│   │   └── settings.py        # Configuration management
│   ├── models/
│   │   ├── video.py          # Video data models
│   │   ├── auth.py           # Authentication data models
│   │   └── ad.py             # Advertisement data models
│   ├── utils/
│   │   └── auth.py            # Authentication utilities
│   ├── middleware/
│   │   └── auth.py            # Authentication middleware
│   ├── services/
│   │   ├── youtube_service.py # YouTube API integration
│   │   └── ads_service.py     # Ads API integration
│   └── main.py               # FastAPI application
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
└── run.sh                   # Startup script
```


## offical documentation
- [FastAPI](https://fastapi.tiangolo.com/)
- [Google Ads API](https://developers.google.com/google-ads/api/docs/start)
- [YouTube Data API](https://developers.google.com/youtube/v3/getting-started)
- [Youtube video](https://developers.google.com/youtube/v3/docs/videos)
- [Youtube search](https://developers.google.com/youtube/v3/docs/search)