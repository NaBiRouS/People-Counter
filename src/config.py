from pathlib import Path


# Root directory of the project
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Input and output directories
INPUT_DIR = PROJECT_ROOT / "data" / "input"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"

# Input video used
VIDEO_PATH = INPUT_DIR / "people_6.mp4"

# YOLO configuration
MODEL_NAME = "yolo11n.pt"
TRACKER_NAME = "fasttrack.yaml"

# COCO class ID for the person class
PERSON_CLASS_ID = 0