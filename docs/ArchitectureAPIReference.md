# ReMap Architecture and API Reference

## Overview

ReMap is a location-based event retrieval system with three core parts:

1. **Fake Event Creation and Geolocalization**  
   Events are synthetically generated and geolocated using Jupyter notebooks for testing vector search.

2. **Backend with FastAPI**  
   Provides APIs for event ingestion, route-based querying, and natural language parsing. Integrates with Qdrant for hybrid dense/sparse vector search with geo and datetime filtering.

3. **Frontend with Streamlit**  
   Offers an interactive UI for manual or natural language route input, displaying routes and events on maps.

---

## Dataset

Fake geolocated event datasets are stored in `dataset/` as JSON files, used for testing Qdrant's similarity and filtering capabilities.

---

## Backend Architecture

### Core Modules

- API routing (`app/api`), service logic (`app/services`), data models (`app/models`), and configuration (`app/core/config.py`).

### Key Components

- **Embeddings:** FastEmbed dense and sparse models for event text.
- **Qdrant Client:** Vector DB with geo and datetime filters.
- **OpenRouteService:** Geocoding and route fetching.
- **CrewAI & Mistral LLM:** Natural language to structured query extraction.

### Services

- **Event Ingestion:** Async geocoding, embedding, deduplication, batch upserts.
- **Qdrant Queries:** Geo-filtering coupled with hybrid vector search and date constraints.
- **Route Service:** Geocodes and buffers routes.
- **Extraction Service:** CrewAI agent extracts structured payloads from sentences with strict validation.

### Data Flow

1. User inputs route or NL query.  
2. Backend geocodes and buffers route.  
3. NL input is parsed into a payload.  
4. Qdrant queried for matching events.  
5. Route and filtered events returned.

---

## API Reference

### POST /create_map

Create route-based event map.

**Request:**  
- origin_address, destination_address  
- buffer_distance (km), startinputdate, endinputdate  
- query_text, numevents, profile_choice

**Response:**  
- route_coords, buffer_polygon  
- origin and destination coords + address  
- sorted nearby events with geo and address info

### POST /ingestevents

Upload JSON event file for ingestion.

**Request:**  
- Multipart/form-data `.json`

**Response:**  
- Ingestion counts and collection info

### POST /sentencetopayload

Parse natural language sentence to event query payload.

**Request:**  
- JSON with `sentence`

**Response:**  
- Extracted structured fields or error if invalid

---

## Frontend Architecture

- Streamlit UI, OpenLayers map, connects to backend APIs for routes and extraction.
- Supports manual and natural language input modes with filtering options.

---

## Notes

- Efficient event retrieval via geo, datetime, and hybrid vector filtering in Qdrant.
- Modular backend services and reactive frontend support extensibility.
