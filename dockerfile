# Use the official lightweight Python base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required by OpenCV and FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch
# The separate PyTorch CPU index prevents pip from downloading
# NVIDIA CUDA libraries that are not needed in this container
RUN pip install \
    --no-cache-dir \
    --default-timeout=300 \
    torch==2.13.0+cpu \
    torchvision==0.28.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Copy backend dependencies
COPY requirements-api.txt .

# Install the remaining Python dependencies
RUN pip install \
    --no-cache-dir \
    --default-timeout=300 \
    -r requirements-api.txt

# Copy the application source code
COPY src ./src

# Create directories used by the application
RUN mkdir -p data/uploads data/output

# Start the FastAPI server
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]