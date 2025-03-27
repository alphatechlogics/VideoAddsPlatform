# Development Guide

## Setup Development Environment

1. **Create Virtual Environment**

2. **Install Dependencies**

3. **Configure Environment**
Create `.env` file with required API keys and tokens.

## Project Structure Explanation

### Core Components

1. **Services (`app/services/`)**
   - `youtube_service.py`: Handles YouTube API integration
     - Video search
     - Category mapping
     - Channel resolution
   - `ads_service.py`: Manages advertisement-related operations
     - Video ad search
     - Ad metadata retrieval

2. **Models (`app/models/`)**
   - `video.py`: Video data structures
   - `ad.py`: Advertisement data structures

3. **Configuration (`app/config/`)**
   - `settings.py`: Environment and API configuration

4. **API Routes (`app/api/`)**
   - `routes.py`: API endpoint definitions

## Testing

1. **Manual Testing via Swagger UI**
   - Access http://localhost:8000/docs
   - Try out each endpoint
   - Verify responses

2. **Error Handling**
   - Invalid API keys
   - Network issues
   - Rate limiting
   - Invalid parameters

## Common Issues

1. **YouTube API Quotas**
   - Monitor usage
   - Implement caching if needed

2. **Category Mapping**
   - Check category IDs
   - Use fallback categories

3. **Authentication**
   - Verify API keys
   - Check token expiration
