from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

ProfileChoice = Literal["driving-car", "cycling-regular", "foot-walking"]


class RouteRequest(BaseModel):
    origin_address: str = Field(..., example="Padova")
    destination_address: str = Field(..., example="Verona")
    buffer_distance: Optional[float] = Field(default=5.0, example=5.0)  # Optional float with default
    #buffer_distance: int = Field(default=5, example=5)  # default value 5
    startinputdate: datetime = Field(..., example="2025-08-23T13:28:39Z")
    endinputdate: datetime = Field(..., example="2025-08-27T13:28:39Z")
    query_text: Optional[str] = Field(default="", example="Music")
    numevents: Optional[int] = Field(default=100, example=100, description="Number of events to retrieve")  # default 100
    profile_choice: Optional[ProfileChoice] = Field(default="driving-car", example="cycling-regular", description="Transport profile for routing, e.g. 'driving-car', 'cycling-regular'") # default 'driving-car'



class SentenceInput(BaseModel):
    sentence: str = Field(
        ..., 
        example="I want to go from Vicenza to Trento and I will leave 14 September 2025 at 2 a.m. and I will arrive on 11 October at 5:00. Give me 11 events about workshop in a range of 6 km. Use cycling-regular transport."
    )
