import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
from app.models.unlisted_ad import VideoCategory
from fastapi import HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Update Category mapping dictionary with correct values
YOUTUBE_CATEGORIES = {
    "Autos & Vehicles": "12",
    "Comedy": "30",
    "Education": "33",
    "Entertainment": "8",
    "Film & Animation": "18",
    "Gaming": "9",
    "Howto & Style": "6",
    "Movies": "42",
    "Music": "14",
    "N/A": "0",
    "News & Politics": "46",
    "Nonprofits & Activism": "2",
    "People & Blogs": "35",
    "Pets & Animals": "39",
    "Science & Technology": "3",
    "Shorts": "49",
    "Shows": "32",
    "Sports": "7",
    "Trailers": "26",
    "Travel & Events": "19"
}

class UnlistedVideoFinder:
    def __init__(self):
        self.base_url = "https://filmot.com/unlistedSearch"
        self.session = requests.Session()

    def _get_category_id(self, category_name: str) -> Optional[str]:
        """Convert category name to ID."""
        try:
            # Validate category using enum
            category = VideoCategory(category_name)
            return YOUTUBE_CATEGORIES.get(category.value)
        except ValueError:
            logger.warning(f"Invalid category name: {category_name}")
            return None

    def _validate_category(self, category: str) -> bool:
        """Validate if category exists in VideoCategory enum."""
        try:
            VideoCategory(category)
            return True
        except ValueError:
            return False

    def _parse_duration_to_seconds(self, duration: str) -> int:
        """Convert duration string to seconds.
        Handles formats:
        - HHhMMmSSs 
        - MMmSSs
        - SSs
        """
        try:
            # Clean the duration string and remove special characters
            duration = duration.replace('▼', '').replace('▲', '').strip()
            if not duration:
                return 0

            # Initialize counters
            hours = 0
            minutes = 0
            seconds = 0

            # Split into components and process
            components = duration.lower().split()
            for component in components:
                if 'h' in component:
                    hours = int(''.join(filter(str.isdigit, component)))
                elif 'm' in component:
                    minutes = int(''.join(filter(str.isdigit, component)))
                elif 's' in component:
                    seconds = int(''.join(filter(str.isdigit, component)))

            # Calculate total seconds
            total_seconds = (hours * 3600) + (minutes * 60) + seconds
            # logger.debug(f"Parsed duration '{duration}' -> {total_seconds} seconds [h:{hours} m:{minutes} s:{seconds}]")
            return total_seconds

        except Exception as e:
            # logger.debug(f"Error parsing duration '{duration}': {str(e)}")
            return 0

    async def fetch_channel_videos(self, channel_id: str, pages: int = 2) -> List[Dict]:
        """Fetch videos from a specific channel."""
        try:
            params = {
                'sortField': 'viewcount',
                'sortOrder': 'desc',
                'channelID': channel_id
            }
            
            results = []
            
            for page in range(1, pages + 1):
                params['page'] = page
                response = self.session.get(self.base_url, params=params)
                response.raise_for_status()
                
                if not response.text:
                    continue
                    
                soup = BeautifulSoup(response.text, "html.parser")
                rows = soup.find_all('tr')
                
                channel_info = None
                for row in rows:
                    try:
                        # Get channel info from first valid row
                        if not channel_info:
                            channel_td = row.find('td', {'dth': 'Channel'})
                            if channel_td:
                                channel_info = {
                                    'name': channel_td.find('a').text.strip(),
                                    'channel_id': channel_td.find('a')['href'].split('/')[-1],
                                    'subscribers': channel_td.find('small').text.strip() if channel_td.find('small') else "Unknown"
                                }
                        
                        video_data = self._extract_video_data(row)
                        if video_data:
                            if channel_info:
                                video_data.update({
                                    'channel_info': channel_info
                                })
                            results.append(video_data)
                            
                    except Exception as e:
                        logger.error(f"Error processing row: {str(e)}")
                        continue
                        
            return results
            
        except Exception as e:
            logger.error(f"Error fetching channel videos: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def search_unlisted_videos(
        self, 
        keyword: Optional[str] = None, 
        category: Optional[str] = None, 
        channel_id: Optional[str] = None,
        pages: int = 2,
        ads_only: bool = True
    ) -> List[Dict]:
        """
        Search for unlisted videos with filters.
        
        Args:
            keyword: Search term
            category: Video category name (will be converted to ID)
            channel_name: Channel name to filter by
            max_duration: Maximum duration in seconds (default 60 for ads)
            pages: Number of pages to fetch
            ads_only: Filter for short videos (default False)
        """
        if channel_id:
            return await self.fetch_channel_videos(channel_id, pages)

        if category and not self._validate_category(category):
            raise ValueError(f"Invalid category: {category}. Please use one of: {[c.value for c in VideoCategory]}")
        
        results = []
        try:
            # Build search parameters
            params = {
                'sortField': 'viewcount',
                'sortOrder': 'desc',
                'videoDuration': 'short' if ads_only else None  # Add duration filter
            }
            
            if keyword:
                params['search'] = keyword
            if category:
                category_id = self._get_category_id(category)
                if category_id:
                    params['category'] = category_id
            if channel_id:
                params['channelID'] = channel_id

            # Fetch pages
            for page in range(1, pages + 1):
                params['page'] = page
                try:
                    response = self.session.get(self.base_url, params=params)
                    response.raise_for_status()
                    
                    if not response.text:
                        logger.error("Empty response received from server")
                        raise HTTPException(status_code=500, detail="Empty response from server")

                    soup = BeautifulSoup(response.text, "html.parser")
                    table = soup.find('table', class_="table border border-primary table-striped resp-tbl")
                    
                    if not table or not table.find('tbody'):
                        logger.warning(f"No results found for page {page}")
                        continue
                        
                    rows = table.find('tbody').find_all('tr')
                    if not rows:
                        logger.warning(f"No video rows found on page {page}")
                        continue

                    for row in rows:
                        try:
                            video_data = self._extract_video_data(row)
                            if video_data:
                                duration_seconds = video_data.get('duration_seconds', 0)
                                # Skip videos longer than 120 seconds (2 minutes) for ads
                                if ads_only and duration_seconds > 120:
                                    # logger.debug(f"Skipping long video: {duration_seconds}s > 120s")
                                    continue
                                
                                # Validate required fields
                                if all(key in video_data for key in ['title', 'video_id', 'channel_name']):
                                    results.append(video_data)
                                else:
                                    logger.warning(f"Skipping video due to missing fields: {video_data.get('video_id', 'unknown')}")
                        except Exception as row_err:
                            logger.error(f"Error processing row: {str(row_err)}")
                            continue

                except requests.RequestException as e:
                    logger.error(f"Error fetching page {page}: {str(e)}")
                    if not results:  # Only raise if we have no results at all
                        raise HTTPException(status_code=503, detail=f"Error fetching results: {str(e)}")
                    continue

            if not results:
                logger.warning("No videos found matching criteria")
                return []

            logger.info(f"Successfully found {len(results)} videos")
            return results

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            if not results:
                raise HTTPException(status_code=500, detail=str(e))
            return results

    def _extract_video_data(self, row) -> Optional[Dict]:
        """Extract video data from a table row."""
        try:
            title_td = row.find('td', {'dth': 'Title'})
            channel_td = row.find('td', {'dth': 'Channel'})
            
            if not title_td or not channel_td:
                logger.warning("Missing required TD elements")
                return None

            video_link = title_td.find('a')
            if not video_link or 'href' not in video_link.attrs:
                logger.warning("Missing video link")
                return None

            duration_td = row.find('td', {'dth': 'Duration'})
            duration = duration_td.text.strip() if duration_td else "0:00"
            duration_seconds = self._parse_duration_to_seconds(duration)
            # print(f"Parsed duration: {duration} -> {duration_seconds} seconds")

            result = {
                'title': title_td.find('a').text.strip(),
                'video_id': video_link['href'].split('=')[-1],
                'url': video_link['href'],
                'thumbnail': title_td.find('img', class_='lozad')['data-src'] if title_td.find('img', class_='lozad') else "",
                'channel_name': channel_td.find('a').text.strip(),
                'channel_id': channel_td.find('a')['href'].split('/')[-1],
                'subscribers': channel_td.find('small').text.strip() if channel_td.find('small') else "Unknown",
                'category': row.find('td', {'dth': 'Category'}).find('a').text.strip() if row.find('td', {'dth': 'Category'}) else "Unknown",
                'duration': duration,
                'duration_seconds': duration_seconds,
                'views': row.find('td', {'dth': 'Views'}).text.strip() if row.find('td', {'dth': 'Views'}) else "0",
                'likes': row.find('td', {'dth': 'Likes'}).text.strip() if row.find('td', {'dth': 'Likes'}) else "0",
                'dislikes': row.find('td', {'dth': 'Dislikes'}).text.strip() if row.find('td', {'dth': 'Dislikes'}) else "0",
                'upload_date': row.find('td', {'dth': 'Uploaded'}).text.strip() if row.find('td', {'dth': 'Uploaded'}) else "Unknown",
                'languages': {
                    'auto_generated': [img['title'] for img in row.find('td', {'dth': 'Auto-Generated'}).find_all('img')] if row.find('td', {'dth': 'Auto-Generated'}) else [],
                    'subtitles': [img['title'] for img in row.find('td', {'dth': 'Subtitles'}).find_all('img')] if row.find('td', {'dth': 'Subtitles'}) else []
                }
            }

            # Validate required fields
            if not all(result.get(field) for field in ['title', 'video_id', 'channel_name']):
                logger.warning("Missing required fields in extracted data")
                return None

            return result

        except Exception as e:
            logger.error(f"Error extracting video data: {str(e)}")
            return None

    def get_available_categories(self) -> List[str]:
        """Return list of available category names."""
        return [category.value for category in VideoCategory]
