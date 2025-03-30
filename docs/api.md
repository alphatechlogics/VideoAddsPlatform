# API Documentation

Detailed documentation for the Video Ads Platform API endpoints.

## Authentication

### POST /api/auth/register

Register a new user.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "username": "string",
  "email": "string"
}
```

### POST /api/auth/token

Get an access token for API usage. No authentication required.

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Using API Endpoints

All API endpoints require:
1. JWT token in `X-API-Key` header
2. Rate limit: 60 requests per minute per client

**Example Request:**
```bash
# First, get a token
curl -X POST "http://localhost:8000/api/auth/token"

# Use token in requests
curl -X GET "http://localhost:8000/api/search-unlisted" \
     -H "X-API-Key: your.access.token" \
     -H "Content-Type: application/json"
```

**Error Responses:**
```json
{
  "detail": "No token provided. Please include X-API-Key header"
}
```
```json
{
  "detail": "Invalid token format or signature"
}
```
```json
{
  "detail": "Token has expired"
}
```
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

## Video Search

### GET /api/search-videos

Search for YouTube videos with various filters.

**Query Parameters:**
- `keyword` (optional): Search term
- `category` (optional): Video category (e.g., "Music", "Gaming")
- `channel_name` (optional): YouTube channel name

**Response:**
```json
[
  {
    "title": "string",
    "description": "string",
    "video_id": "string",
    "channel_id": "string",
    "url": "string",
    "metadata": {
      "views": 0,
      "likes": 0,
      "comments": 0,
      "upload_date": "2024-01-01T00:00:00Z",
      "categories": ["string"]
    }
  }
]
```

## Unlisted Video Search

### GET /api/search-unlisted

Search for unlisted videos with various filters.

**Query Parameters:**
- `keyword` (optional): Search term
- `category` (optional): Video category from available categories
- `channel_id` (optional): YouTube channel ID
- `ads_only` (optional, default: true): Only return videos suitable for ads

**Response:**
```json
{
  "count": 0,
  "videos": [
    {
      "title": "string",
      "video_id": "string",
      "url": "string",
      "thumbnail": "string",
      "channel_name": "string",
      "channel_id": "string",
      "subscribers": "string",
      "category": "string",
      "duration": "string",
      "views": "string",
      "likes": "string",
      "dislikes": "string",
      "upload_date": "string",
      "languages": {
        "auto_generated": ["string"],
        "subtitles": ["string"]
      },
      "channel_info": {
        "name": "string",
        "channel_id": "string",
        "subscribers": "string"
      }
    }
  ]
}
```

### GET /api/categories

Get available video categories.

**Response:**
```json
{
  "categories": ["string"],
  "total": 0
}
```

## Advertisement Search

### GET /api/search-video-ads

Search for video advertisements on YouTube.

**Query Parameters:**
- `keyword` (optional): Search term
- `category` (optional): Ad category

**Response:**
```json
[
  {
    "ad_id": "string",
    "advertiser": "string",
    "duration": 0,
    "metadata": {
      "title": "string",
      "description": "string",
      "publishedAt": "2024-01-01T00:00:00Z",
      "thumbnail": "string",
      "url": "string"
    },
    "category": "string"
  }
]
```

## Status Endpoints

### GET /api/youtube/status

Check YouTube API connection status.

**Response:**
```json
{
  "status": "connected"
}
```

### GET /api/ads/status

Check Google Ads API connection status.

**Response:**
```json
{
  "status": "connected"
}
```
