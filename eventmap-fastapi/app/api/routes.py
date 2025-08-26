from fastapi import APIRouter, HTTPException
from app.services import openrouteservice_client, qdrant_client
from app.models import schemas
from shapely.geometry import LineString, Point
import geopandas as gpd
import numpy as np
from qdrant_client.http import models as qmodels
from app.core.config import DENSE_MODEL_NAME, SPARSE_MODEL_NAME
from fastembed import TextEmbedding, SparseTextEmbedding


router = APIRouter()

# Initialize embedding models once
dense_embedding_model = TextEmbedding(DENSE_MODEL_NAME)
sparse_embedding_model = SparseTextEmbedding(SPARSE_MODEL_NAME)

@router.post("/create_map")
async def create_event_map(request: schemas.RouteRequest):
    try:
        # Geocode origin and destination
        origin_point = openrouteservice_client.geocode_address(request.origin_address)
        destination_point = openrouteservice_client.geocode_address(request.destination_address)
        coords = [origin_point, destination_point]

        # Get route geometry with user-selected transport profile
        routes = openrouteservice_client.get_route(coords, profile=request.profile_choice)
        route_geometry = routes['features'][0]['geometry']
        route_coords = route_geometry['coordinates']
        
        # Create route line and buffer polygon
        route_line = LineString(route_coords)
        route_gdf = gpd.GeoDataFrame([{'geometry': route_line}], crs='EPSG:4326')
        route_gdf_3857 = route_gdf.to_crs(epsg=3857)
        buffer_polygon = route_gdf_3857.buffer(request.buffer_distance * 1000).to_crs(epsg=4326).iloc[0]
        polygon_coords = np.array(buffer_polygon.exterior.coords).tolist()
        polygon_coords_qdrant = [{"lon": lon, "lat": lat} for lon, lat in polygon_coords]

        # Build geographic filter for Qdrant
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

        # Build date intersection filter for Qdrant
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
            must=geo_filter.must + date_intersection_filter.must
        )

        # Embed query text to dense and sparse vectors
        query_dense_vector = list(dense_embedding_model.passage_embed([request.query_text]))[0].tolist()
        query_sparse_embedding = list(sparse_embedding_model.passage_embed([request.query_text]))[0]

        # Query Qdrant hybrid search with filter
        payloads = qdrant_client.query_events_hybrid(
            dense_vector=query_dense_vector,
            sparse_vector=query_sparse_embedding,
            query_filter=final_filter,
            collection_name="veneto_events",
            limit=request.numevents,
        )

        if not payloads:
            return {"message": "No events found in Qdrant for this route/buffer and date range."}

        # Sort events by projected distance along route
        def distance_along_route(event):
            point = Point(event['location']['lon'], event['location']['lat'])
            return route_line.project(point)
        
        sorted_events = sorted(payloads, key=distance_along_route)

        # Add lat/lon/address top-level keys for frontend convenience
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
