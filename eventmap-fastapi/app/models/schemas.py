from pydantic import BaseModel, Field
from datetime import datetime

class RouteRequest(BaseModel):
    origin_address: str = Field(..., example="Padova")
    destination_address: str = Field(..., example="Verona")
    buffer_distance: int = Field(..., example=5)
    startinputdate: datetime = Field(..., example="2025-08-23T13:28:39Z")
    endinputdate: datetime = Field(..., example="2025-08-27T13:28:39Z")

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "origin_address": "Padova",
    #             "destination_address": "Verona",
    #             "buffer_distance": 5,
    #             "startinputdate": "2025-08-23T13:28:39Z",
    #             "endinputdate": "2025-08-27T13:28:39Z"
    #         }
    #     }
