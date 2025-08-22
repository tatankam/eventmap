from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.core.config import QDRANT_URL, QDRANT_API_KEY

qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=2000000)

def query_events(polygon_coords_qdrant, collection_name="veneto_events", limit=100):
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
    results = qdrant_client.query_points(
        collection_name=collection_name,
        limit=limit,
        query_filter=geo_filter,
        with_payload=True
    )
    return [p.payload for p in results.points]
