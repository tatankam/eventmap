from pydantic import BaseModel
from datetime import datetime

class RouteRequest(BaseModel):
    origin_address: str
    destination_address: str
    buffer_distance: int
    startinputdate: datetime 
    endinputdate: datetime    
