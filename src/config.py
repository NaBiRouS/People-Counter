import os
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables from the .env file
load_dotenv()

# FastAPI backend URL used by the Streamlit frontend
API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
)

PUBLIC_API_URL = os.getenv(
    "PUBLIC_API_URL",
    "http://127.0.0.1:8000"
)

# Directory where uploaded videos are temporarily stored
UPLOAD_DIR = Path("data/uploads")

# Directory where processed videos are stored
OUTPUT_DIR = Path("data/output")

# YOLO model used for person detection
MODEL_NAME = "yolo11n.pt"

# Tracker configuration used by YOLO
TRACKER_NAME = "fasttrack.yaml"
