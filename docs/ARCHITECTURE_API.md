# Architecture and API Reference

## Overview 🌐

The **ReMap** project consists of three main components:

1. **Fake Event Creation and Geolocalization**  
   📍 Events are generated and geolocated using Jupyter notebooks (`notebooks/01_eda_events.ipynb`).

2. **Backend with FastAPI**  
   ⚙️ Provides API endpoints for event ingestion, route-based event querying, and natural language payload extraction. Integrates with **Qdrant** vector database for semantic and geospatial querying.

3. **Frontend with Streamlit**  
   🖥️ Interactive UI enabling manual or natural language-based route inputs. Communicates with backend APIs to create routes and retrieve relevant events.

---

## Backend Architecture ⚙️

### Core Modules 🧱

- `app/api` — FastAPI routers managing HTTP endpoints.  
- `app/services` — Business logic layer (event ingestion, embeddings, geocoding, Qdrant querying).  
- `app/models` — Pydantic schemas for data validation and serialization.  
- `app/core/config.py` — Configuration (constants and environment variables).

### Key Backend Components 🧩

- **Embedding Models**  
  🧠 Uses FastEmbed's **dense** and **sparse** models for semantic text embedding (`DENSE_MODEL_NAME`, `SPARSE_MODEL_NAME`).

- **Qdrant Client**  
  📊 Connects to Qdrant vector DB, supporting hybrid (vector + keyword) search with geo-filtering.

- **API Endpoints**:

  - `POST /createmap` — Generate route, search nearby events, return sorted list and geometry.  
  - `POST /ingestevents` — Upload and ingest JSON event files to Qdrant with deduplication.  
  - `POST /sentencetopayload` — Convert natural language into structured query parameters.

### Data Flow 🔄

1. User request triggers map creation or event ingestion.  
2. Backend geocodes addresses using **OpenRouteService**.  
3. Events are retrieved or stored in **Qdrant** using vector search and geospatial/date filters.  
4. JSON responses return event lists, route coordinates, and buffer polygons.

---

## Frontend Architecture 🖼️

### Technologies 🛠️

- **Streamlit** for reactive frontend UI.  
- **OpenLayers** for map rendering, embedded using HTML components.  
- Connects to backend via `API_URL` environment variable, switching between manual and natural language modes.

### Main Components 🔧

- `streamlit_app.py` — Entry point and UI logic.  
- Supports:
  - Manual form input  
  - Natural language input (e.g., “Find events between Paris and Berlin this weekend”)  
- Interacts with backend for:
  - Route generation  
  - Payload extraction from user queries  
- Displays:
  - Interactive route map  
  - Events as styled markers  
  - Filters for date, transport profile, keywords, and number of events

---

## Dataset 📂

Event datasets reside in the `dataset/` directory as geolocated, structured `.json` files.  
⚠️ These are **fake events**, used for **testing Qdrant's vector and geo-query capabilities**.

---

## API Reference 📡

### `POST /createmap` — Route-Based Event Map

Generates route and fetches relevant events from origin to destination.

#### 🔸 Request Body Schema (`schemas.RouteRequest`):

- `origin_address`: *string*  
- `destination_address`: *string*  
- `buffer_distance`: *float* (in km)  
- `startinputdate`: *ISO8601 datetime string*  
- `endinputdate`: *ISO8601 datetime string*  
- `query_text`: *string*  
- `numevents`: *integer*  
- `profile_choice`: *string* ("car", "bike", "walking")

#### 🔹 Response:

- `route_coords`: List of coordinates forming the route  
- `buffer_polygon`: Buffer polygon around the route  
- `origin`: Latitude/longitude of origin  
- `destination`: Latitude/longitude of destination  
- `events`: List of sorted event objects near the route

---

### `POST /ingestevents` — Upload & Ingest Events 📥

Ingest a batch of events from a `.json` file into Qdrant.

#### 🔸 Request:

- `multipart/form-data` with attached `.json` file.

#### 🔹 Response:

- Summary of ingestion (number of events, deduplicated entries)  
- Qdrant collection info

---

### `POST /sentencetopayload` — NLP to Query Payload 📝

Parses user’s natural language sentence into structured query format.

#### 🔸 Request:

- `sentence`: *string*

#### 🔹 Response:

- Extracted fields: origin, destination, buffer distance, dates, keywords, number of events, profile choice (as JSON payload)

---

## Natural Language Extraction via LLM & CrewAI 🧠

The backend integrates **CrewAI** and **Mistral LLM** to enable intelligent extraction of query parameters from natural language.

### Core Components:

- **LLM Setup**  
  🤖 Configured via environment variables (`MODEL_NAME`, `BASE_URL`, `API_KEY`), using **zero temperature** for deterministic responses.

- **Agent**  
  🎯 CrewAI `Agent` with the role: `"Payload Extractor"`, designed to return a strict JSON payload schema containing:

  - `origin_address`  
  - `destination_address`  
  - `buffer_distance`  
  - `startinputdate`  
  - `endinputdate`  
  - `query_text`  
  - `numevents`  
  - `profile_choice`

- **Task + Crew**  
  🧩 Task wraps the extraction objective with schema constraints.  
  👥 Crew ensures the task runs to completion with structured output.

### Service Function: `extract_payload(sentence: str)` 📤

- Invokes `crew.kickoff()` with the sentence.  
- Validates output against `Payload` Pydantic schema.  
- Returns valid JSON or `None` on failure.

### Benefits 💡

- Enhances `/sentencetopayload` endpoint to support **flexible, unstructured user queries**.  
- Converts user-friendly input (e.g., "Find me concerts along my trip from Berlin to Munich next weekend") into strict backend-compatible parameters.  
- Ensures **schema validation** and consistent user experience powered by **AI and vector search**.

---

## Notes 🗒️

- ⚡ The backend uses Qdrant's hybrid search (dense + sparse) and geo-filtering to efficiently fetch relevant events.  
- 🧩 Frontend leverages **Streamlit's session state** for reactive, smooth user experience.  
- 🧱 Designed for extensibility — new endpoints, models, and UI features can be added easily.
