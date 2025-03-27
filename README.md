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
  - Duration-based filtering
- RESTful API endpoints
- Swagger/OpenAPI documentation
- Automatic category mapping
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

### Videos
- `GET /api/search-videos`
  - Query params: keyword, category, channel_name
  - Returns list of videos with metadata

### Advertisements
- `GET /api/search-video-ads`
  - Query params: keyword, category
  - Returns list of video advertisements

### Status
- `GET /api/youtube/status` - YouTube API connection status
- `GET /api/ads/status` - Google Ads API connection status

## Project Structure
```
video and ads/
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── config/
│   │   └── settings.py        # Configuration management
│   ├── models/
│   │   ├── video.py          # Video data models
│   │   └── ad.py             # Advertisement data models
│   ├── services/
│   │   ├── youtube_service.py # YouTube API integration
│   │   └── ads_service.py     # Ads API integration
│   └── main.py               # FastAPI application
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
└── run.sh                   # Startup script
```
