from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.core.config import QDRANT_SERVER, QDRANT_API_KEY, COLLECTION_NAME


qdrant_client = QdrantClient(url=QDRANT_SERVER, api_key=QDRANT_API_KEY, timeout=2000000)


def query_events(polygon_coords_qdrant, query_filter=None, collection_name=COLLECTION_NAME, limit=100):
    if query_filter is None:
        # default geo filter only
        query_filter = qmodels.Filter(
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
        query_filter=query_filter,
        with_payload=True
    )
    return [p.payload for p in results.points]


def query_events_hybrid(dense_vector, sparse_vector, query_filter, collection_name=COLLECTION_NAME, limit=100):
    results = qdrant_client.query_points(
        collection_name=collection_name,
        prefetch=[
            qmodels.Prefetch(
                query=qmodels.SparseVector(
                    indices=list(sparse_vector.indices),
                    values=list(sparse_vector.values)
                ),
                using="sparse_vector",
                limit=50,
            ),
            qmodels.Prefetch(
                query=dense_vector,
                using="dense_vector",
                limit=50,
            ),
        ],
        query=qmodels.FusionQuery(fusion=qmodels.Fusion.RRF),
        query_filter=query_filter,
        limit=limit,
        with_payload=True
    )
    return [p.payload for p in results.points]
