from pathlib import Path
from uuid import uuid4

from src.config import OUTPUT_DIR, UPLOAD_DIR
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.services.job_manager import JobManager


app = FastAPI(
    title="People Counter API",
    description="API for people detection, tracking, and counting.",
    version="1.0.0",
)


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


job_manager = JobManager()


@app.get("/health")
def health_check() -> dict:
    """
    Checks whether the API is running.

    Args:
        None.

    Returns:
        A dictionary indicating that the API is healthy.
    """
    return {"status": "ok"}


@app.post("/process-video")
def process_video_endpoint(file: UploadFile = File(...)) -> dict:
    """
    Uploads a video and starts a background processing job.

    Args:
        file: Video uploaded by the client.

    Returns:
        A dictionary containing the newly created job ID.

    Raises:
        HTTPException: If the uploaded file format is unsupported.
    """
    allowed_extensions = {".mp4", ".avi", ".mov", ".mkv"}

    file_extension = Path(file.filename or "").suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported video format.",
        )

    input_id = uuid4().hex
    input_path = UPLOAD_DIR / f"{input_id}{file_extension}"

    # Save the uploaded video
    with input_path.open("wb") as buffer:
        while chunk := file.file.read(1024 * 1024):
            buffer.write(chunk)

    # Start processing in the background
    job_id = job_manager.create_job(
        input_path=input_path,
        output_dir=OUTPUT_DIR,
    )

    return {
        "status": "queued",
        "job_id": job_id,
    }


@app.get("/jobs/{job_id}")
def get_job_status(job_id: str) -> dict:
    """
    Returns the current status and results of a processing job.

    Args:
        job_id: Unique identifier of the processing job.

    Returns:
        A dictionary containing the job status and results.

    Raises:
        HTTPException: If the job does not exist.
    """
    job = job_manager.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    response = {
        "job_id": job.job_id,
        "status": job.status,
    }

    if job.status == "completed":
        response.update(
            {
                "entries": job.entries,
                "exits": job.exits,
            }
        )

    if job.status == "failed":
        response["error"] = job.error

    return response


@app.get("/videos/{job_id}")
def download_processed_video(job_id: str) -> FileResponse:
    """
    Returns a completed processed video.

    Args:
        job_id: Unique identifier of the completed job.

    Returns:
        A FileResponse containing the processed MP4 video.

    Raises:
        HTTPException: If the processed video does not exist.
    """
    output_path = OUTPUT_DIR / f"{job_id}_processed.mp4"

    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Processed video not found.",
        )

    return FileResponse(
        path=output_path,
        media_type="video/mp4",
        filename=f"{job_id}_processed.mp4",
    )