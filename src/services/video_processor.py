import subprocess
from pathlib import Path

import cv2

from src.config import MODEL_NAME, TRACKER_NAME
from src.counting.counter import PeopleCounter
from src.detection.detector import PersonDetector
from src.pipeline.processor import PeopleCounterPipeline


def convert_to_browser_format(input_path: Path, output_path: Path) -> None:
    """
    Converts a video to H.264 MP4 format using FFmpeg so that it can be
    played reliably by web browsers.

    Args:
        input_path: Path to the source video.
        output_path: Path where the converted video will be saved.

    Returns:
        None.

    Raises:
        RuntimeError: If FFmpeg fails during conversion.
    """
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output_path),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg conversion failed:\n{result.stderr}"
        )


def process_video(input_path: Path, output_path: Path) -> dict:
    """
    Processes a video through the people detection, tracking, and counting
    pipeline and saves a browser-compatible annotated video.

    Args:
        input_path: Path to the input video.
        output_path: Path where the processed video will be saved.

    Returns:
        A dictionary containing the total number of entries and exits.
    """
    # Create the person detector and tracker
    detector = PersonDetector(
        model_name=MODEL_NAME,
        tracker_name=TRACKER_NAME,
    )

    # Open the input video
    cap = cv2.VideoCapture(str(input_path))

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {input_path}")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Create a temporary path for the OpenCV-generated video
    temporary_path = output_path.with_name(
        f"{output_path.stem}_temp.mp4"
    )

    temporary_path.parent.mkdir(parents=True, exist_ok=True)

    # OpenCV writes the intermediate video using mp4v
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        str(temporary_path),
        fourcc,
        fps,
        (frame_width, frame_height),
    )

    # Create the people counter
    counter = PeopleCounter(line_x=frame_width // 2)

    # Create the reusable CV pipeline
    pipeline = PeopleCounterPipeline(
        detector=detector,
        counter=counter,
    )

    while True:
        # Read the next frame
        success, frame = cap.read()

        if not success:
            break

        # Process the frame through detection, tracking, and counting
        annotated_frame, _ = pipeline.process_frame(frame)

        # Write the annotated frame to the temporary video
        writer.write(annotated_frame)

    # Release OpenCV resources before FFmpeg accesses the file
    cap.release()
    writer.release()

    # Convert the temporary video to browser-compatible H.264 MP4
    convert_to_browser_format(
        input_path=temporary_path,
        output_path=output_path,
    )

    # Remove the temporary OpenCV video
    if temporary_path.exists():
        temporary_path.unlink()

    return {
        "entries": counter.entries,
        "exits": counter.exits,
    }