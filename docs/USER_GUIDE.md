
# User Guide

## Introduction

Welcome to the **Event Map** project! This application allows you to visualize events along a route using a combined backend and frontend system. The backend provides API services, and the frontend offers an interactive UI built with Streamlit.

## System Requirements

- Docker and Docker Compose installed (for easy deployment)  
- Python 3.13+ if running locally without Docker

## Installation

### Using Docker Compose (recommended)

1. Clone the repository:

    ```bash
    git clone <repo-url>
    cd <repo-folder>
    ```

2. Build and run all services:

    ```bash
    docker compose up --build
    ```

### Local Setup (optional)

1. Create and activate a Python virtual environment.

2. Install backend dependencies:

    ```bash
    pip install -r backend/requirements.txt
    ```

3. Install frontend dependencies:

    ```bash
    pip install -r frontend/requirements.txt
    ```

4. Follow backend and frontend startup instructions in respective folders.

## Getting Started

### Running the App

- Access the frontend UI in your browser: [http://localhost:8501](http://localhost:8501)  
- Backend API is reachable at: [http://localhost:8000](http://localhost:8000)

### User Interface Overview

- Input addresses and travel profile manually or input natural language travel plans.
- Specify buffer distance, date ranges, and query text to filter events.
- Events are displayed interactively on the map along the travel route.

## Core Features Usage

### Creating an Event Map

1. Enter origin and destination addresses or write a natural language sentence describing your route.
2. Set buffer radius (in km) to limit event search area.
3. Choose transport profile (car, bike, walking).
4. Set date and time ranges to filter event schedules.
5. Submit and explore generated events on the interactive map.

### Uploading Event Files

1. Use the backend `/ingestevents` API to upload JSON event files.
2. Events will be indexed in the Qdrant vector store for fast retrieval.

### Natural Language Query

Use the frontend's natural language input mode to describe travel plans naturally, like:

> "I want to go from Vicenza to Trento leaving 2 September 2025 at 2 a.m., arriving 18 October 2025 at 5 a.m., and show me 10 music events within 6 km using bike."

## Data Management

All event datasets are stored in the `dataset/` folder and processed in notebooks under `notebooks/`. New datasets can be added and ingested via the API.

## Troubleshooting

- Ensure Docker is running and ports 8000 and 8501 are free.
- Check backend logs for errors during event ingestion or route creation.
- Clear browser cache if frontend UI behaves unexpectedly.

## FAQs

**Q:** Can I use the backend API independently?  
**A:** Yes, the API is fully accessible via HTTP endpoints documented in `ARCHITECTURE_API.md`.

**Q:** How do I contribute to the project?  
**A:** See the contributing guidelines in `CONTRIBUTING.md`.

## Contact and Support

For issues or questions, please open an issue on the GitHub repository.

---

Thank you for using **Event Map**!  
Happy mapping and discovery!
