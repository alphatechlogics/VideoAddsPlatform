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

Get authentication token.

**Request Body (form-data):**
- `username`: string
- `password`: string

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Using API Endpoints

All API endpoints (except authentication endpoints) require:
1. JWT token in `X-API-Key` header
2. Rate limit: 60 requests per minute per client

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/search-videos" \
     -H "X-API-Key: your.jwt.token" \
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
