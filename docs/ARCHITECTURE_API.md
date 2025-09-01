# Architecture and API Reference

## Overview

The Event Map project consists of three main components:

1. **Fake Event Creation and Geolocalization**  
   Events are generated and geolocated using Jupyter notebooks (`notebooks/01_eda_events.ipynb`).
   
2. **Backend with FastAPI**  
   Provides API endpoints for event ingestion, route-based event querying, and natural language payload extraction. The backend integrates with Qdrant vector database for storing and querying event vectors.
   
3. **Frontend with Streamlit**  
   Interactive UI allowing users to input travel routes manually or via natural language. It connects to the backend APIs for route creation and event retrieval.

---

## Backend Architecture

### Core Modules

- `app/api` — FastAPI router modules handling HTTP endpoints.
- `app/services` — Service layer implementing logic such as event ingestion, geocoding, embeddings, and Qdrant query handling.
- `app/models` — Pydantic schemas for data validation and serialization.
- `app/core/config.py` — Configuration constants and environment variables.

### Key Backend Components

- **Embedding Models:**  
  Uses FastEmbed's dense and sparse text embedding models (`DENSE_MODEL_NAME`, `SPARSE_MODEL_NAME`) for semantic search.

- **Qdrant Client:**  
  Interface with Qdrant vector database supporting hybrid search with dense and sparse embeddings.

- **Endpoints:**

  - `POST /create_map`  
    Creates a route map from origin and destination addresses, buffers events along the route in Qdrant filtered by geography and date, and returns sorted events.

  - `POST /ingestevents`  
    Accepts JSON event files, ingests events into Qdrant with batching and deduplication.

  - `POST /sentencetopayload`  
    Parses natural language input and extracts structured event query parameters.

### Data Flow

1. User request triggers map creation or ingestion.
2. Backend geocodes addresses using OpenRouteService.
3. Queries or ingest data into Qdrant using vector and geospatial filters.
4. Returns JSON responses with event lists and route geometry.

---

## Frontend Architecture

### Technologies

- Streamlit for reactive, single-page frontend.
- Uses OpenLayers for map visualization embedded through HTML component.
- Connects to backend API via environment variable `API_URL`.

### Main Components

- `streamlit_app.py` — Main entry point and UI logic.
- User modes: manual input or natural language input.
- Calls backend APIs for route creation and parameter extraction.
- Displays events and routes on interactive map with popups, styled markers, and filters.
- Supports date and time range, transport profile, query text, and number of events parameters.

---

## Dataset

Events datasets reside in `dataset/`, containing geolocated and structured event files in JSON format, ingested into Qdrant for searching.

---

## API Reference

### POST /create_map

Creates a route-based event map.

**Request Body Schema:** (`schemas.RouteRequest`)

- `origin_address`: string
- `destination_address`: string
- `buffer_distance`: float (km)
- `startinputdate`: ISO8601 datetime string
- `endinputdate`: ISO8601 datetime string
- `query_text`: string
- `numevents`: integer
- `profile_choice`: string (e.g., "car", "bike", "walking")

**Response:**

- `route_coords`: list of coordinates forming the route
- `buffer_polygon`: list of buffer polygon coordinates
- `origin`: lat/lon origin point
- `destination`: lat/lon destination point
- `events`: list of event objects along route, sorted by position on route

### POST /ingestevents

Ingests events from a JSON file upload into Qdrant.

**Request:** Multipart/form-data with `.json` file.

**Response:** Ingestion summary and collection info.

### POST /sentencetopayload

Parses a natural language sentence into a structured event query payload.

**Request:**

- `sentence`: string

**Response:**

- Extracted fields matching event query parameters.

---

## Notes

- The backend heavily relies on Qdrant's geo and hybrid vector filtering for efficient event retrieval.
- The frontend relies on Streamlit’s session state and reactive components for seamless user experience.
- This architecture supports easy extension with additional endpoints and frontend features.

