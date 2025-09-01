# EventRouteFinder 🗺️🔍

EventRouteFinder is a powerful and interactive event discovery platform designed to help users find relevant events along a custom travel route. By combining semantic similarity search on event descriptions with dynamic geospatial and temporal filtering, it provides personalized event recommendations visualized on an interactive map.

---

## Features

- Store events enriched with metadata such as title, description, venue, address, latitude, and longitude.
- Leverage sparse and dense embeddings of event descriptions stored in the Qdrant vector database for advanced semantic similarity search.
- Seamlessly merge similarity search results with multiple filters including:
  - Geospatial filtering within a user-defined buffer distance (km) around a route.
  - Temporal filtering through start and end date/time travel windows.
  - Textual similarity based on user query inputs.
  - Transport profile-based routing (e.g., driving, cycling, walking) via OpenRouteService.
  - Limit results by number of events retrieved.
- Calculate travel routes using OpenRouteService API, considering different travel modes.
- Interactive frontend built with Streamlit and Folium for:
  - Displaying the calculated route and buffer zone on an interactive map.
  - Marking matched events with detailed popups along or nearby the route.
  - Providing an expandable event list panel with full event details.
- Validated input handling to avoid invalid date/time ranges and other errors.

---

## How It Works

1. User inputs:
   - Origin and destination addresses plus transport profile (e.g., driving, cycling).
   - Buffer distance defining how far from the route to search for events.
   - Search query text enabling semantic similarity matching on event descriptions.
   - Travel time window with start and end date/time.
   - Number of events to retrieve.
2. The backend calculates the optimized route based on input travel profile.
3. It runs a merged query combining:
   - Semantic similarity search over event embeddings.
   - Geo-filtering to only include events within the buffer zone polygon around the route.
   - Temporal filtering restricting events to specified travel windows.
4. Frontend renders an interactive map showing the route, buffer polygon, and event markers.
5. Event list panel provides detailed descriptions and timing info.
6. Input errors or inconsistencies are clearly communicated on the frontend.

---

## Technology Stack

- [Qdrant](https://qdrant.tech/) vector database for storing event embeddings and enabling similarity search with geo-filters.
- Sparse and dense embedding models encoding event descriptions for rich semantic queries.
- [OpenRouteService](https://openrouteservice.org/) APIs for route calculation and transport profile support.
- [Streamlit](https://streamlit.io/) for rapid frontend development.
- [Openstreetmap](https://www.openstreetmap.org/) for advanced interactive maps.
- Python backend (FastAPI suggested) serving route computation and event querying APIs.
- Geopandas and Shapely for geographic calculations and buffering routes.
- Docker for containerization of the fastapi and streamlit

---

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/tatankam/eventmap.git
    cd eventmap/eventmap-fastapi
    ```
2. Install dependencies (preferably in a virtual environment):
    ```
    pip install -r requirements.txt
    ```
3. Start the backend API server:
    ```
    uvicorn app.main:app --reload
    ```
4. Launch the Streamlit frontend app :
    ```
    cd /eventmap/frontend
    streamlit run streamlit_app.py
    ```

---

## Usage

- Enter origin and destination addresses in the frontend.
- Select your transport profile (driving, cycling, walking).
- Specify the buffer distance in kilometers around the route.
- Enter a text search query to find semantically relevant events.
- Set the travel start and end date/time window.
- Choose how many events to retrieve.
- Click "Search Events" to generate and visualize the route plus event markers.
- Explore matched events on the map and in the detailed event list.

---

## Demo

[![Watch the Demo](https://github.com/tatankam/eventmap/blob/main/video/thumbail.jpg)](https://youtu.be/BiKDhHpg0BQ)

---

## Roadmap & Future Improvements

- Natural language input parsing for query parameters via an AI assistant (e.g., Mistral).
- Multi-point and waypoint support in route planning.
- Adding event type/category embeddings and filters for finer search control.
- Enhanced UX with smoother interfaces and richer map interactions.
- create a UI to enter events
- create random id instead of sequential and if the id is busy, regenerate the id
- adjust documentation

---
### Dockerize

See Dockerfile for streamlit and eventmap-fastapi
docker compose 
../event_map$ docker compose up --build --force-recreate if you failed before
Else docker compose up 
docker compose down to close
You have to execute from there because it finds app.main:app and it works and .env
The slow behavior observed when using docker compose down followed by docker compose up likely happens because docker compose down stops and removes the containers, which means that on the subsequent docker compose up, the containers and resources (including embedding models) are re-initialized or re-downloaded.

To avoid this, consider these options:

Use docker compose restart instead of down/up, which stops and starts the containers without removing them. This keeps the container state and cached data intact, greatly improving start-up speed.

If you need to update containers but want to keep volumes and downloads persistent, avoid down or use volumes to persist data like models outside the container file system.

Consider volume mounting or caching strategies for your models or data so they are not downloaded every time a container is recreated.

This approach optimizes performance by preventing unnecessary re-downloads and reinitializations during restarts or redeployments with Docker Compose.

The first time you have to:
docker compose up -d

To be sure, if you did some build, do this:
docker compose build --no-cache
and after do this:
docker compose up -d


Next you use (it is good even if yoi modify docker compose file)
docker compose stop
docker compose start
or
docker compose restart 


this is if you don't modify code, because if you use docker compose down, it remove container so it is really slow to docker compose up


---

## License

This project is licensed under the MIT License.

---

## Contact

For questions or suggestions, contact the project owner or open an issue on GitHub.

---

Discover events like never before — happy exploring! 🗺️🔍
