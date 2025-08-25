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
from qdrant_client.http import models as qmodels

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

        # Build geo filter
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

        # Build date intersection filter using input dates from request
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

        # Combine geo and date filters
        final_filter = qmodels.Filter(
            must=[
                geo_filter,
                date_intersection_filter
            ]
        )

        # Query events using qdrant client and pass the final combined filter
        payloads = qdrant_client.query_events(
            polygon_coords_qdrant=polygon_coords_qdrant,
            query_filter=final_filter,
            collection_name="veneto_events",
            limit=100
        )

        df = pd.json_normalize(payloads)
        if df.empty:
            return """
            <div style="padding: 30px; color: #B22222; font-size: 18px;">
                No events found in Qdrant for this route/buffer and date range.
            </div>
            """

        # Calculate distance to sort events
        def distance_along_route(row):
            event_point = Point(row['location.lon'], row['location.lat'])
            return route_line.project(event_point)
        df['distance_along_route'] = df.apply(distance_along_route, axis=1)
        df.sort_values('distance_along_route', inplace=True)

        map_center = [(origin_point[1] + destination_point[1]) / 2, (origin_point[0] + destination_point[0]) / 2]
        m = folium.Map(location=map_center, zoom_start=9, zoom_control=True, scrollWheelZoom=False, dragging=False, height="100%")
        folium.PolyLine(locations=[(lat, lon) for lon, lat in route_coords], color='blue', weight=5).add_to(m)
        folium.GeoJson(buffer_polygon.__geo_interface__, style_function=lambda x: {'color': 'red', 'fillOpacity': 0.1}).add_to(m)
        folium.Marker(location=[origin_point[1], origin_point[0]], icon=folium.DivIcon(html='<div style="font-size: 16pt; color: #006400; font-weight: bold; text-shadow: 1px 1px 1px rgba(0,0,0,0.5);">🚦 Start</div>')).add_to(m)
        folium.Marker(location=[destination_point[1], destination_point[0]], icon=folium.DivIcon(html='<div style="font-size: 16pt; color: #B22222; font-weight: bold; text-shadow: 1px 1px 1px rgba(0,0,0,0.5);">🏁 End</div>')).add_to(m)

        map_html = m._repr_html_()

        event_list_html = """
        <div style="width: 400px; height: 450px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;">
        <h3>Event List on the route</h3><ul style="list-style-type: none; padding-left: 0;">
        """

        for _, row in df.iterrows():
            title = row.get('title', 'No Name')
            address = row.get('location.address', '')
            description = row.get('description', '')
            start_date = row.get('start_date', '')
            end_date = row.get('end_date', '')
            event_list_html += f"<li style='margin-bottom: 10px;'><strong>{title}</strong><br>{description}</br><br>{address}</br><br>Data Inizio:{start_date}</br><br>Data Fine: {end_date}</br></br></li>"

        event_list_html += "</ul></div>"

        combined_html = f"""
        <style>
            /* Adjust folium map container size */
            .folium-map {{
                width: 800px !important;
                height: 450px !important;
            }}
            /* Scroll container for horizontal scrollbar */
            .map-scroll-container {{
                width: 650px;
                height: 350px;
                overflow-x: auto;
                overflow-y: auto;
                white-space: nowrap;
            }}
        </style>
        <div style="display: flex; gap: 20px; align-items: flex-start;">
            <div class="map-scroll-container">{map_html}</div>
            <div style="height: 450px;">{event_list_html}</div>
        </div>
        """

        return combined_html

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
