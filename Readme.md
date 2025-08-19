# Event on a Route

## Overview

This project allows you to list and visualize events that occur along a route between two or more points. The main features include:

- Define a multi-stop geographic route (e.g., from Point A to Point B, with optional waypoints).
- Draw the route on a map.
- Add a buffer zone (e.g., 1 km) around the route to represent the area of interest.
- Store event data in [Qdrant](https://qdrant.tech/), a vector database that supports geo queries.
- Query and list events located within the buffered area of the route.

## Technology Stack

- **Python** for scripting and data handling.
- **Geopandas** and **Shapely** for geographic calculations and buffering.
- **Qdrant** for storing event data with geospatial payload and vector search capabilities.
- **Qdrant Python client** to interact with the Qdrant database via API.
- (Optional) **Folium/Leaflet** or other mapping libraries for route visualization.

## How It Works

1. Define the route as a list of longitude-latitude tuples covering start, optional waypoints, and end.
2. Create a `LineString` object from the route points.
3. Use `Geopandas` with a projected coordinate reference system (CRS) to create an accurate buffer polygon around the route.
4. Convert the buffer polygon coordinates into a format accepted by Qdrant’s geo filtering.
5. Insert your events into Qdrant with the location stored as latitude and longitude payload fields.
6. Use Qdrant’s geo filtering capability to query all events falling within the buffered polygon around the route.
7. Display or process the resulting events according to your application needs.

## Sample Usage

