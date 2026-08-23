import cv2

from src.counting.counter import CrossingEvent, PeopleCounter
from src.detection.detector import PersonDetector
from src.detection.results import extract_tracked_people


class PeopleCounterPipeline:
    """
    Combines detection, tracking, and people counting into one reusable
    processing pipeline.

    Args:
        detector: PersonDetector responsible for detecting and tracking people.
        counter: PeopleCounter responsible for detecting crossing events.

    Returns:
        A PeopleCounterPipeline instance.
    """

    def __init__(self, detector: PersonDetector, counter: PeopleCounter):
        self.detector = detector
        self.counter = counter

    def process_frame(self, frame) -> tuple[any, list[CrossingEvent]]:
        """
        Processes one video frame through detection, tracking, and counting.

        Args:
            frame: OpenCV image/frame in BGR format.

        Returns:
            A tuple containing the annotated frame and a list of new crossing
            events detected in this frame.
        """

        # Detect and track people in the current frame
        results = self.detector.track(frame)

        # Convert YOLO results into the clean format expected by the counter
        tracked_people = extract_tracked_people(results)

        # Update the counter and retrieve newly detected crossing events
        new_events = self.counter.update(tracked_people)

        # Draw bounding boxes and tracking IDs
        annotated_frame = results[0].plot()

        # Draw the counting line
        cv2.line(
            annotated_frame,
            (self.counter.line_x, 0),
            (self.counter.line_x, annotated_frame.shape[0]),
            (0, 255, 255),
            2,
        )

        # Display the current entry/exit totals
        cv2.putText(
            annotated_frame,
            f"IN: {self.counter.entries}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        cv2.putText(
            annotated_frame,
            f"OUT: {self.counter.exits}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
        )

        return annotated_frame, new_events