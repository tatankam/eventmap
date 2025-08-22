from pydantic import BaseModel

class RouteRequest(BaseModel):
    origin_address: str
    destination_address: str
    buffer_distance: int

