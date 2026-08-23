import cv2

from src.config import MODEL_NAME, TRACKER_NAME, VIDEO_PATH
from src.detection.detector import PersonDetector
from src.counting.counter import PeopleCounter
from src.pipeline.processor import PeopleCounterPipeline


def main():
    # Create the person detector and tracker
    detector = PersonDetector(
        model_name=MODEL_NAME,
        tracker_name=TRACKER_NAME,
    )

    # Open the input video
    cap = cv2.VideoCapture(str(VIDEO_PATH))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {VIDEO_PATH}")

    # Get the video width so that we can place the counting line
    # in the center of the frame
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    # Create the people counter
    counter = PeopleCounter(line_x=frame_width // 2)

    # Combine detection, tracking, and counting
    pipeline = PeopleCounterPipeline(
        detector=detector,
        counter=counter,
    )

    while True:
        # Read the next frame from the video
        success, frame = cap.read()

        if not success:
            break

        # Process the frame through the complete CV pipeline
        annotated_frame, new_events = pipeline.process_frame(frame)

        # Print any new crossing events
        for event in new_events:
            print(
                f"Person {event.track_id} crossed {event.direction} "
                f"at {event.timestamp.strftime('%H:%M:%S')}"
            )

        # Display the processed frame
        cv2.imshow("People Counter", annotated_frame)

        # Press q to stop the program
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the video and close the OpenCV window
    cap.release()
    cv2.destroyAllWindows()





if __name__ == "__main__":
    main()