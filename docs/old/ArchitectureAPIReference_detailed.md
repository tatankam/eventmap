# ReMap Architecture and API Reference

## Overview

ReMap is a location-based event retrieval project consisting of three main components:

1. **Fake Event Creation and Geolocalization**  
   Synthetic events are created and geolocated using Jupyter notebooks (`notebooks/01_eda_events.ipynb`) to test vector search capabilities.

2. **Backend with FastAPI**  
   Exposes REST API endpoints for event ingestion, querying events along routes, and converting natural language input into structured search payloads. Integrates with Qdrant vector database supporting hybrid dense and sparse vector search with geographic and time filtering.

3. **Frontend with Streamlit**  
   Provides a reactive single-page app where users enter routes manually or via natural language, interacting seamlessly with the backend to visualize routes and events on an interactive map.

---

## Fake Event Creation and Geolocalization Dataset

The event datasets reside in the `dataset/` folder, containing geolocated, structured fake events in JSON format. They facilitate testing Qdrant’s search similarity and complex filtering features along travel routes.

---

## Backend Architecture

### Core Modules

- `app/api`: FastAPI router modules managing HTTP endpoints.
- `app/services`: Implements ingestion, geocoding, embedding, natural language extraction, and Qdrant querying logic.
- `app/models`: Pydantic data validation and serialization schemas.
- `app/core/config.py`: Configuration constants and environment variables.

### Key Backend Components

- **Embedding Models:** Utilizes FastEmbed’s dense and sparse embedding models to build semantic representations of event descriptions for hybrid vector search.

- **Qdrant Vector Database:** Maintains event collections with vector and payload indexing that supports efficient geo, datetime, and semantic filtering.

- **OpenRouteService Client:** Provides address geocoding and route retrieval according to user-selected transport profiles.

- **CrewAI and Mistral LLM Integration:**  
  Integrates the Mistral large language model via CrewAI to parse unstructured natural language input into structured event query payloads. This involves:

  - Loading model and API keys from environment variables.
  - A CrewAI agent specifically designed to extract fields such as origin/destination addresses, buffer distances, start/end date-times, query keywords, event counts, and profile choices.
  - Validation of these extracted fields using Pydantic models, enforcing default values and ensuring logical date sequences.
  - Definition of extraction tasks and sequential execution managed by Crew for reliable parsing.
  - The `extract_payload(sentence: str)` function interfaces with this pipeline, producing validated query payloads or handling errors gracefully.

### Main Backend Services

#### Event Ingestion Service

- Loads events from JSON files.
- Asynchronously geocodes venue locations using OpenStreetMap’s Nominatim.
- Generates dense and sparse embeddings for event text.
- Uses content hashing to avoid redundant upserts and performs batch insertion into Qdrant.
- Ensures required Qdrant collections and payload indexes exist prior to ingestion.

#### Qdrant Query Client

- Executes geo-filtered queries within route buffer polygons.
- Performs hybrid dense and sparse vector search with optional relevance score thresholds.
- Applies date/time range filters to retrieve events active during the requested period.
- Returns enriched payloads with relevance scoring.

#### OpenRouteService Client

- Translates addresses into geographic coordinates.
- Requests optimized routes with user-defined profile settings (e.g., driving, cycling, walking).
- Supports generating buffer polygons around route lines.

#### Extraction Service

- Utilizes CrewAI and the Mistral LLM to transform natural language inputs into structured query objects.
- Ensures extracted payloads conform to strict schema validations.
- Safely manages parsing errors and returns usable query parameters for API consumption.

### Data Flow Summary

1. User provides route and query details or natural language input.
2. Backend geocodes addresses and generates travel route with buffer.
3. Natural language sentences are parsed into detailed query payloads by CrewAI + Mistral LLM.
4. Qdrant is queried for events matching geographic, temporal, and semantic criteria.
5. API returns route geometries and sorted, filtered event data.

---

## API Reference

### POST /create_map

Generates a route-based event map with filtered events.

**Request (schemas.RouteRequest):**
- `origin_address`: string
- `destination_address`: string
- `buffer_distance`: float (km)
- `startinputdate`: ISO8601 datetime string
- `endinputdate`: ISO8601 datetime string
- `query_text`: string
- `numevents`: integer
- `profile_choice`: string (e.g., "car", "bike", "walking")

**Response:**
- `route_coords`: list of route coordinate pairs
- `buffer_polygon`: coordinates defining the buffered area
- `origin` and `destination`: lat/lon with provided addresses
- `events`: list of events sorted by their position along the route, each including location and address details

### POST /ingestevents

Uploads and ingests event data from JSON files.

**Request:** Multipart/form-data file upload with `.json`.

**Response:** Provides ingestion statistics including inserted, updated, skipped counts, and current collection information.

### POST /sentencetopayload

Parses natural language query sentences into structured event query payloads.

**Request:** JSON containing a `sentence` string.

**Response:** JSON object with extracted payload fields or HTTP 400 on extraction/validation failure.

---

## Frontend Architecture

- Uses Streamlit for a responsive interface and OpenLayers for map rendering.
- Supports manual and natural language travel route input.
- Dynamically displays routes and events with filtering controls.
- Communicates with backend via configurable API endpoints.

---

## Notes

- Combines geographic, temporal, and hybrid vector filtering in Qdrant for scalable, accurate event retrieval.
- Modular design supports easy extension and robust backend/frontend integration.
