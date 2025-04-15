import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")

# Vector Database Configuration
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "data/vector_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Application Configuration
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Security Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Data paths
SAMPLE_EVENTS_PATH = os.getenv("SAMPLE_EVENTS_PATH", "data/sample_events.json")
