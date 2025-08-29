from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import ORJSONResponse
from app.api.routes import router  # Absolute import

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(default_response_class=ORJSONResponse)  # Use ORJSON for faster JSON responses

app.include_router(router)

# app.mount("/static", StaticFiles(directory="app/static"), name="static")

origins = [
    "http://localhost:8501",  # Streamlit's default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)