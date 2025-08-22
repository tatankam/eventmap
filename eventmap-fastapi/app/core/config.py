from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../.env")

OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
