from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import routes
from fastapi.responses import ORJSONResponse

app = FastAPI(default_response_class=ORJSONResponse) # Use ORJSON for faster JSON responses

app.include_router(routes.router)

#app.mount("/static", StaticFiles(directory="app/static"), name="static")

from fastapi.middleware.cors import CORSMiddleware

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
