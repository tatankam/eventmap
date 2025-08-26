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

## On Eventbrite.ipynb there is the model

## See fastapi app

## TO DO List
* natural language to parameters (with Mistral)
* CrewAI for sequential tools from the functions in the notebook

* ingesting type/category with vectors embedding so I can search for similarity
* Choose a smooth interface
* put credits to openroute it it isn't yet
* insert multipoint on the route
* query with date and category as well


## How to start uvicorn
cd /event_map/eventmap-fastapi
uvicorn app.main:app --reload

To see the FastApi docs: http://127.0.0.1:8000/docs
To test the fastapi app: http://127.0.0.1:8000/static/index.html

Per interrogare ovvero filtrare un singolo punto nella dashboard di Qdrant:
GET collections

// Get collection info
GET collections/collection_name

// List points in a collection, using filter
POST /collections/veneto_events/points/scroll
{
  "filter": {
    "must": [
      {
        "has_id": [425]
      }
    ]
  },
  "limit": 1
}

I did sparse and dense I loaded, so I created frontend with all parmeters

To Do: crewai for natural query to json for the fastapi
Choose from manual parameter and natural query
Create flow, draw the flow
Document hot to install as docker
1) fastapi container
2) streamlit container
3) crewai docker and use mistral as LLM local or openrouter in chatopenai format so it is agnostic
Load fresh data in a extend region
TO DO: route with byke or car ?
