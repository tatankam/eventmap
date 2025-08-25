from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import routes

app = FastAPI()

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
