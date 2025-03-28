from pydantic import BaseModel, Field
from typing import Dict, Optional

class Ad(BaseModel):
    ad_id: str
    advertiser: str
    duration: int = 0
    metadata: Dict = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
