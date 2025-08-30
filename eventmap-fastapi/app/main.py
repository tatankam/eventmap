from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from app.api.routes import router  # Absolute import

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(default_response_class=ORJSONResponse)  # Use ORJSON for faster JSON responses

app.include_router(router)

# CORS settings
origins = [
    "*"  # "http://localhost:8501",  # you could set Streamlit's default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)