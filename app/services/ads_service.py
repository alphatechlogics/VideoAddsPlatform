from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from app.config.settings import settings
from app.models.ad import Ad
from typing import List
from fastapi import HTTPException
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GoogleAdsService:
    def __init__(self):
        try:
            # Clean and format the customer ID
            customer_id = str(settings.google_ads_login_customer_id).replace('-', '')
            
            
            config = {
                'developer_token': settings.google_ads_developer_token,
                'client_id': settings.google_ads_client_id,
                'client_secret': settings.google_ads_client_secret,
                'refresh_token': settings.google_ads_refresh_token,
                'login_customer_id': customer_id,
                'use_proto_plus': True,
                'version': 'v13'  # Specify API version
            }
            
            logger.debug("Initializing Google Ads client...")
            self.client = GoogleAdsClient.load_from_dict(config)
            logger.info("Google Ads client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize Google Ads client: {str(e)}"
            )

    async def search_ads(self, keyword: str = None, category: str = None) -> List[Ad]:
        try:
            logger.debug(f"Searching ads with keyword: {keyword}, category: {category}")
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Build the GAQL query
            query_conditions = []
            if keyword:
                query_conditions.append(f"ad_group_criterion.keyword.text LIKE '%{keyword}%'")
            if category:
                query_conditions.append(f"campaign.advertising_channel_type = '{category}'")

            where_clause = " AND ".join(query_conditions) if query_conditions else "1=1"
            
            query = f"""
            SELECT
                ad_group_ad.ad.id,
                ad_group_ad.ad.name,
                ad_group_ad.ad.type,
                ad_group_ad.ad.final_urls,
                ad_group.id,
                ad_group.name,
                campaign.id,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros
            FROM ad_group_ad
            WHERE {where_clause}
            LIMIT 50
            """
            
            # logger.debug(f"Executing GAQL query: {query}")
            
            # Execute search request with cleaned customer_id
            customer_id = str(settings.google_ads_login_customer_id).replace('-', '')
            response = ga_service.search(
                customer_id=customer_id,
                query=query
            )

            # Process results
            ads = []
            for row in response:
                try:
                    ad = Ad(
                        ad_id=str(row.ad_group_ad.ad.id),
                        advertiser=str(row.ad_group.name),
                        duration=0,
                        metadata={
                            "type": str(row.ad_group_ad.ad.type_),
                            "final_urls": list(row.ad_group_ad.ad.final_urls),
                            "impressions": int(row.metrics.impressions),
                            "clicks": int(row.metrics.clicks),
                            "cost_micros": int(row.metrics.cost_micros)
                        },
                        category=category or "undefined"
                    )
                    ads.append(ad)
                except Exception as e:
                    logger.error(f"Error processing ad row: {str(e)}")
                    continue

            logger.info(f"Successfully fetched {len(ads)} ads")
            return ads

        except GoogleAdsException as ex:
            logger.error(f"Request with ID '{ex.request_id}' failed with status "
                        f"'{ex.error.code().name}' and includes the following errors:")
            for error in ex.failure.errors:
                logger.error(f"\tError with message '{error.message}'.")
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        logger.error(f"\t\tOn field: {field_path_element.field_name}")
            raise HTTPException(status_code=400, detail=str(ex.failure.errors[0].message))
        
        except Exception as e:
            logger.error(f"Unexpected error in search_ads: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error while fetching ads data")