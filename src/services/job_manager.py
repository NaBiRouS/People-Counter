from dataclasses import dataclass
from pathlib import Path
from threading import Thread
from uuid import uuid4

from src.services.video_processor import process_video
from src.monitoring.metrics import (
    VIDEOS_PROCESSED, VIDEOS_FAILED,
    PEOPLE_ENTRIES, PEOPLE_EXITS,
    PROCESSING_TIME,
    ACTIVE_JOBS,
)


@dataclass
class VideoJob:
    """
    Stores the state and results of one video-processing job.

    Args:
        job_id: Unique identifier for the job.
        status: Current job status.
        entries: Number of detected entries.
        exits: Number of detected exits.
        output_path: Path to the processed video.
        error: Error message if processing fails.

    Returns:
        A VideoJob object.
    """

    job_id: str
    status: str = "queued"
    entries: int = 0
    exits: int = 0
    output_path: str | None = None
    error: str | None = None


class JobManager:
    """
    Manages background video-processing jobs.

    Args:
        None.

    Returns:
        A JobManager instance.
    """

    def __init__(self):
        # Store jobs in memory using their unique job IDs
        self.jobs: dict[str, VideoJob] = {}

    def create_job(self, input_path: Path, output_dir: Path) -> str:
        """
        Creates and starts a background video-processing job.

        Args:
            input_path: Path to the uploaded input video.
            output_dir: Directory where the processed video will be saved.

        Returns:
            The unique job ID.
        """
        # Generate the single ID that identifies this processing job
        job_id = uuid4().hex

        # Use the job ID for the output filename as well
        output_path = output_dir / f"{job_id}_processed.mp4"

        job = VideoJob(
            job_id=job_id,
            output_path=str(output_path),
        )

        self.jobs[job_id] = job

        # Start video processing in a background thread
        thread = Thread(
            target=self._process_job,
            args=(job, input_path, output_path),
            daemon=True,
        )

        thread.start()

        return job_id


    def _process_job(self, job: VideoJob, input_path: Path, output_path: Path) -> None:
        """
        Processes a video in a background thread and updates its job state.

        Args:
            job: VideoJob being processed.
            input_path: Path to the uploaded video.
            output_path: Path where the processed video will be saved.

        Returns:
            None.
        """
        ACTIVE_JOBS.inc()
        
        try:
            job.status = "processing"

            with PROCESSING_TIME.time():
                results = process_video(
                    input_path=input_path,
                    output_path=output_path,
                )

            job.entries = results["entries"]
            PEOPLE_ENTRIES.inc(job.entries)
            job.exits = results["exits"]
            PEOPLE_EXITS.inc(job.exits)
            job.status = "completed"
            VIDEOS_PROCESSED.inc()

        except Exception as exc:
            job.status = "failed"
            VIDEOS_FAILED.inc()
            job.error = str(exc)

        finally:
            ACTIVE_JOBS.dec()
            
            # Remove the original uploaded video after processing
            if input_path.exists():
                input_path.unlink()

    def get_job(self, job_id: str) -> VideoJob | None:
        """
        Retrieves a job by its unique ID.

        Args:
            job_id: Unique identifier of the requested job.

        Returns:
            The VideoJob if it exists, otherwise None.
        """
        return self.jobs.get(job_id)