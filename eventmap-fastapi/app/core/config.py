from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../.env")

OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")
QDRANT_SERVER = os.getenv("QDRANT_SERVER")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Add dense and sparse model names to config
DENSE_MODEL_NAME = os.getenv("DENSE_MODEL_NAME")
SPARSE_MODEL_NAME = os.getenv("SPARSE_MODEL_NAME")
COLLECTION_NAME = "veneto_events"