from ultralytics import YOLO


class PersonDetector:
    """
    Detects and tracks people in video frames using YOLO.

    Args:
        model_name: Name or path of the YOLO model to load.
        tracker_name: Name of the tracker configuration to use.

    Returns:
        A PersonDetector instance configured for person detection and tracking.
    """

    def __init__(self, model_name: str, tracker_name: str):
        self.model = YOLO(model_name)
        self.tracker_name = tracker_name

    def track(self, frame):
        """
        Detects and tracks people in a single video frame.

        Args:
            frame: OpenCV image/frame in BGR format.

        Returns:
            YOLO tracking results for the current frame.
        """
        return self.model.track(
            frame,
            persist=True, # keep the tracker state across frames (like the id)
            classes=[0], # detect the person class (class ID 0 in COCO dataset)
            tracker=self.tracker_name,
            verbose=False,
        )