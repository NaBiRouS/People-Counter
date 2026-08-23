def extract_tracked_people(results) -> list[dict]:
    """
    Extracts person tracking IDs and centroid coordinates from YOLO results.

    Args:
        results: YOLO tracking results returned by the detector.

    Returns:
        A list of dictionaries containing each person's tracking ID and
        centroid coordinates.
    """
    tracked_people = []

    result = results[0]

    # if no objects were tracked
    if result.boxes.id is None:
        return tracked_people

    boxes = result.boxes.xyxy.cpu().numpy()
    track_ids = result.boxes.id.int().cpu().tolist()
    classes = result.boxes.cls.int().cpu().tolist()

    for box, track_id, class_id in zip(boxes, track_ids, classes):

        # only people class
        if class_id != 0:
            continue

        x1, y1, x2, y2 = box

        # calculate center of the bounding box
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        tracked_people.append(
            {
                "track_id": track_id,
                "centroid": (center_x, center_y),
            }
        )

    return tracked_people