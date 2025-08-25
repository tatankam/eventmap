from fastapi import APIRouter, HTTPException
from app.services import openrouteservice_client, qdrant_client
from app.models import schemas
from shapely.geometry import LineString, Point
import geopandas as gpd
import numpy as np
from qdrant_client.http import models as qmodels

router = APIRouter()

@router.post("/create_map")
async def create_event_map(request: schemas.RouteRequest):
    try:
        origin_point = openrouteservice_client.geocode_address(request.origin_address)
        destination_point = openrouteservice_client.geocode_address(request.destination_address)
        coords = [origin_point, destination_point]
        routes = openrouteservice_client.get_route(coords)
        route_geometry = routes['features'][0]['geometry']
        route_coords = route_geometry['coordinates']
        route_line = LineString(route_coords)
        route_gdf = gpd.GeoDataFrame([{'geometry': route_line}], crs='EPSG:4326')
        route_gdf_3857 = route_gdf.to_crs(epsg=3857)
        buffer_polygon = route_gdf_3857.buffer(request.buffer_distance * 1000).to_crs(epsg=4326).iloc[0]
        polygon_coords = np.array(buffer_polygon.exterior.coords).tolist()
        polygon_coords_qdrant = [{"lon": lon, "lat": lat} for lon, lat in polygon_coords]

        geo_filter = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="location",
                    geo_polygon=qmodels.GeoPolygon(
                        exterior=qmodels.GeoLineString(points=polygon_coords_qdrant)
                    )
                )
            ]
        )

        date_intersection_filter = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="start_date",
                    range=qmodels.DatetimeRange(
                        lte=request.endinputdate,
                    )
                ),
                qmodels.FieldCondition(
                    key="end_date",
                    range=qmodels.DatetimeRange(
                        gte=request.startinputdate,
                    )
                )
            ],
        )

        final_filter = qmodels.Filter(
            must=[
                geo_filter,
                date_intersection_filter
            ]
        )

        payloads = qdrant_client.query_events(
            polygon_coords_qdrant=polygon_coords_qdrant,
            query_filter=final_filter,
            collection_name="veneto_events",
            limit=100
        )

        if not payloads:
            return {"message": "No events found in Qdrant for this route/buffer and date range."}

        # Sort events by distance along the route
        def distance_along_route(event):
            point = Point(event['location']['lon'], event['location']['lat'])
            return route_line.project(point)
        sorted_events = sorted(payloads, key=distance_along_route)
        # Add lat/lon address top-level keys from nested location for frontend convenience
        for event in sorted_events:
            loc = event.get('location', {})
            event['address'] = loc.get('address')
            event['lat'] = loc.get('lat')
            event['lon'] = loc.get('lon')

        response = {
            "route_coords": route_coords,
            "buffer_polygon": polygon_coords,
            "origin": {"lat": origin_point[1], "lon": origin_point[0]},
            "destination": {"lat": destination_point[1], "lon": destination_point[0]},
            "events": sorted_events
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
