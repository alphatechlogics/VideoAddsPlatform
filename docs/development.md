# Development Guide

## Setup Development Environment

1. **Create Virtual Environment**

2. **Install Dependencies**

3. **Configure Environment**
Create `.env` file with required API keys and tokens:
```env
YOUTUBE_API_KEY=your_youtube_api_key
JWT_SECRET_KEY=your_jwt_secret_key

```

## Authentication Flow

1. **Token Generation**
   - Call `/api/auth/token` to get a new token
   - No credentials required

2. **API Access**
   - Include token in `X-API-Key` header
   - Handle token expiration (30 minutes)
   - Respect rate limiting (60 req/min)

3. **Token Format**
   ```json
   {
     "exp": "expiration timestamp",
     "iat": "issued at timestamp",
     "type": "access",
     "jti": "unique token id"
   }
   ```

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
   - `unlisted_ads_service.py`: Manages unlisted advertisement operations
     - Unlisted ad search
     - Ad metadata retrieval

2. **Models (`app/models/`)**
   - `video.py`: Video data structures
   - `ad.py`: Advertisement data structures
   - `unlisted_ad.py`: Unlisted advertisement data structures
   - `auth.py`: Authentication data structures

3. **Configuration (`app/config/`)**
   - `settings.py`: Environment and API configuration

4. **API Routes (`app/api/`)**
   - `routes.py`: API endpoint definitions
   - `auth.py`: Authentication routes

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

## Security Considerations

1. **Token Management**
   - Store JWT secret securely
   - Rotate tokens periodically
   - Never expose tokens in logs

2. **Rate Limiting**
   - Monitor usage patterns
   - Adjust limits as needed
   - Implement IP-based blocking

3. **Error Handling**
   - Invalid tokens
   - Expired tokens
   - Rate limit exceeded

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
