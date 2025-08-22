#!/bin/bash

PROJECT_NAME="eventmap-fastapi"

mkdir -p $PROJECT_NAME/app/api
mkdir -p $PROJECT_NAME/app/core
mkdir -p $PROJECT_NAME/app/services
mkdir -p $PROJECT_NAME/app/models
mkdir -p $PROJECT_NAME/app/static
mkdir -p $PROJECT_NAME/tests

# Create __init__.py in subfolders
touch $PROJECT_NAME/app/__init__.py
touch $PROJECT_NAME/app/api/__init__.py
touch $PROJECT_NAME/app/core/__init__.py
touch $PROJECT_NAME/app/services/__init__.py
touch $PROJECT_NAME/app/models/__init__.py

# Create core/config.py
cat > $PROJECT_NAME/app/core/config.py << EOF
from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
EOF

# Create services/openrouteservice_client.py
cat > $PROJECT_NAME/app/services/openrouteservice_client.py << EOF
import openrouteservice
from app.core.config import OPENROUTE_API_KEY

ors_client = openrouteservice.Client(key=OPENROUTE_API_KEY)

def geocode_address(address: str):
    geocode_result = ors_client.pelias_search(text=address)
    if geocode_result and 'features' in geocode_result and len(geocode_result['features']) > 0:
        coords = geocode_result['features'][0]['geometry']['coordinates']
        return tuple(coords)
    else:
        raise ValueError(f"Could not geocode address: {address}")

def get_route(coords, radiuses=[1000, 1000]):
    return ors_client.directions(coordinates=coords, profile='driving-car', radiuses=radiuses, format='geojson')
EOF

# Create services/qdrant_client.py
cat > $PROJECT_NAME/app/services/qdrant_client.py << EOF
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
EOF

# Create models/schemas.py
cat > $PROJECT_NAME/app/models/schemas.py << EOF
from pydantic import BaseModel

class RouteRequest(BaseModel):
    origin_address: str
    destination_address: str
    buffer_distance: int

EOF

# Create api/routes.py
cat > $PROJECT_NAME/app/api/routes.py << EOF
from fastapi import APIRouter, HTTPException
from app.services import openrouteservice_client, qdrant_client
from app.models import schemas
from shapely.geometry import LineString
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import pandas as pd
import folium
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.post("/create_map", response_class=HTMLResponse)
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
        payloads = qdrant_client.query_events(polygon_coords_qdrant)
        df = pd.json_normalize(payloads)

        # Calculate distance to sort events
        def distance_along_route(row):
            event_point = Point(row['location.lon'], row['location.lat'])
            return route_line.project(event_point)
        df['distance_along_route'] = df.apply(distance_along_route, axis=1)
        df.sort_values('distance_along_route', inplace=True)

        map_center = [(origin_point[1] + destination_point[8]) / 2, (origin_point + destination_point) / 2]
        m = folium.Map(location=map_center, zoom_start=9, zoom_control=False, scrollWheelZoom=False, dragging=False, height=450)
        folium.PolyLine(locations=[(lat, lon) for lon, lat in route_coords], color='blue', weight=5).add_to(m)
        folium.GeoJson(buffer_polygon.__geo_interface__, style_function=lambda x: {'color': 'red', 'fillOpacity': 0.1}).add_to(m)
        folium.Marker(location=[origin_point[1], origin_point], icon=folium.DivIcon(html='<div style="font-size: 16pt; color: #006400; font-weight: bold; text-shadow: 1px 1px 1px rgba(0,0,0,0.5);">🚦 Start</div>')).add_to(m)
        folium.Marker(location=[destination_point[1], destination_point], icon=folium.DivIcon(html='<div style="font-size: 16pt; color: #B22222; font-weight: bold; text-shadow: 1px 1px 1px rgba(0,0,0,0.5);">🏁 End</div>')).add_to(m)

        map_html = m._repr_html_()

        event_list_html = """
        <div style="width: 400px; height: 450px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;">
        <h3>Event List on the route</h3><ul style="list-style-type: none; padding-left: 0;">
        """
        for _, row in df.iterrows():
            title = row.get('title', 'No Name')
            description = row.get('description', '')
            address = row.get('location.address', '')
            event_list_html += f"<li style='margin-bottom: 10px;'><strong>{title}</strong><br>{description}</br><br>{address}</br></br></li>"
        event_list_html += "</ul></div>"

        combined_html = f"""
        <div style="display: flex; gap: 20px; align-items: flex-start;">
        <div style="flex: 1; min-width: 600px; height: 450px;">{map_html}</div>
        <div style="height: 450px;">{event_list_html}</div>
        </div>
        """

        return combined_html

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
EOF

# Create app/main.py
cat > $PROJECT_NAME/app/main.py << EOF
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import routes

app = FastAPI()

app.include_router(routes.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

EOF

# Create app/static/index.html (basic frontend template)
cat > $PROJECT_NAME/app/static/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Event Map</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        label { display: block; margin-top: 10px; }
        #map-events { display: flex; gap: 20px; margin-top: 20px; }
        #map-container, #event-list { border: 1px solid #ccc; padding: 10px; }
        #map-container { flex: 2; min-width: 600px; height: 450px; }
        #event-list { flex: 1; height: 450px; overflow-y: scroll; }
    </style>
</head>
<body>
    <h1>Event Map</h1>
    <form id="search-form">
        <label>Origin Address: <input type="text" id="origin" value="Borgo Trento, Verona, Italy" size="50"></label>
        <label>Destination Address: <input type="text" id="destination" value="Piazza dei Signori, Treviso, Italy" size="50"></label>
        <label>Buffer Distance (km): 
            <select id="buffer">
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3" selected>3</option>
                <option value="5">5</option>
                <option value="10">10</option>
            </select>
        </label>
        <button type="submit">Create Map</button>
    </form>
    <div id="map-events"></div>

    <script>
        const form = document.getElementById('search-form');
        const mapEventsDiv = document.getElementById('map-events');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const origin = document.getElementById('origin').value;
            const destination = document.getElementById('destination').value;
            const buffer = document.getElementById('buffer').value;

            mapEventsDiv.innerHTML = "Loading...";

            try {
                const response = await fetch('/create_map', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        origin_address: origin,
                        destination_address: destination,
                        buffer_distance: parseInt(buffer),
                    }),
                });
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const html = await response.text();
                mapEventsDiv.innerHTML = html;
            } catch (error) {
                mapEventsDiv.innerHTML = "Error: " + error.message;
            }
        });
    </script>
</body>
</html>
EOF

# Create requirements.txt
cat > $PROJECT_NAME/requirements.txt << EOF
fastapi
uvicorn[standard]
python-dotenv
openrouteservice
qdrant-client
geopandas
pandas
shapely
folium
jinja2
EOF

echo "Project $PROJECT_NAME created with FastAPI structure and example files."
echo "To run: cd $PROJECT_NAME && uvicorn app.main:app --reload"
