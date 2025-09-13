from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.ingest_service import ingest_events_from_file
from app.services import openrouteservice_client, qdrant_client
from app.models import schemas
from shapely.geometry import LineString, Point
import geopandas as gpd
import numpy as np
from qdrant_client.http import models as qmodels
from app.core.config import DENSE_MODEL_NAME, SPARSE_MODEL_NAME, COLLECTION_NAME
from fastembed import TextEmbedding, SparseTextEmbedding
import os
import shutil

# Import the extraction function and Pydantic models
from app.services.extraction_service import extract_payload
from app.models.schemas import SentenceInput
from pydantic import ValidationError
from fastapi import HTTPException

router = APIRouter()

# Initialize embedding models once for reuse
dense_embedding_model = TextEmbedding(DENSE_MODEL_NAME)
sparse_embedding_model = SparseTextEmbedding(SPARSE_MODEL_NAME)


@router.post("/create_map")
async def create_event_map(request: schemas.RouteRequest):
    try:
        origin_point = openrouteservice_client.geocode_address(request.origin_address)
        destination_point = openrouteservice_client.geocode_address(request.destination_address)
        coords = [origin_point, destination_point]

        routes = openrouteservice_client.get_route(coords, profile=request.profile_choice)
        route_geometry = routes['features'][0]['geometry']
        route_coords = route_geometry['coordinates']
        if len(route_coords) < 2:
            raise HTTPException(status_code=400, detail="Route must contain two different address for buffering.")

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
                    range=qmodels.DatetimeRange(lte=request.endinputdate)
                ),
                qmodels.FieldCondition(
                    key="end_date",
                    range=qmodels.DatetimeRange(gte=request.startinputdate)
                )
            ]
        )

        final_filter = qmodels.Filter(must=geo_filter.must + date_intersection_filter.must)

        score_treshold = 0.0
        if request.query_text.strip() == "":
            score_treshold = 0.0  # No text query, so no score threshold
        else:
            score_treshold = 0.34  # Adjust based on desired relevance I found 0.34 to be a good balance

        query_dense_vector = list(dense_embedding_model.passage_embed([request.query_text]))[0].tolist()
        query_sparse_embedding = list(sparse_embedding_model.passage_embed([request.query_text]))[0]

        payloads = qdrant_client.query_events_hybrid(
            dense_vector=query_dense_vector,
            sparse_vector=query_sparse_embedding,
            query_filter=final_filter,
            collection_name=COLLECTION_NAME,
            limit=request.numevents,
            score_threshold=score_treshold  # Optional: filter out low-score results
        )

        if not payloads:
            return {"message": "No events found in Qdrant for this route/buffer and date range."}

        def distance_along_route(event):
            point = Point(event['location']['lon'], event['location']['lat'])
            return route_line.project(point)

        sorted_events = sorted(payloads, key=distance_along_route)

        for event in sorted_events:
            loc = event.get('location', {})
            event['address'] = loc.get('address')
            event['lat'] = loc.get('lat')
            event['lon'] = loc.get('lon')


        response = {
            "route_coords": route_coords,
            "buffer_polygon": polygon_coords,
            "origin": {"lat": origin_point[1], "lon": origin_point[0], "address": request.origin_address},
            "destination": {"lat": destination_point[1], "lon": destination_point[0], "address": request.destination_address},
            "events": sorted_events
        }



        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ingestevents")
async def ingest_events_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only .json files are accepted")

    save_dir = "/tmp"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, file.filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = await ingest_events_from_file(save_path)
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)

    return {
        "filename": file.filename,
        "inserted": result["inserted"],
        "updated": result["updated"],
        "skipped_unchanged": result["skipped_unchanged"],
        "collection_info": str(result["collection_info"]),
    }


@router.post("/sentencetopayload")
async def sentence_to_payload(data: SentenceInput):
    sentence = data.sentence
    try:
        output = extract_payload(sentence)
        if output:
            return output.model_dump()
        else:
            raise HTTPException(status_code=400, detail="Failed to extract valid payload or validation error")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        # Other unexpected errors
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
