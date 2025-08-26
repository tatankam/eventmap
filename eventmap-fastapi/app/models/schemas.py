from pydantic import BaseModel, Field
from datetime import datetime

class RouteRequest(BaseModel):
    origin_address: str = Field(..., example="Padova")
    destination_address: str = Field(..., example="Verona")
    buffer_distance: int = Field(..., example=5)
    startinputdate: datetime = Field(..., example="2025-08-23T13:28:39Z")
    endinputdate: datetime = Field(..., example="2025-08-27T13:28:39Z")
    query_text: str = Field(..., example="Music")
    numevents: int = Field(100, example=100, description="Number of events to retrieve")
    profile_choice: str = Field(..., example="cycling-regular", description="Transport profile for routing, e.g. 'driving-car', 'cycling-regular'")
