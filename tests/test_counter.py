from src.counting.counter import PeopleCounter


def create_person(track_id: int, x: int, y: int = 100) -> dict:
    """
    Creates a tracked-person dictionary for testing.

    Args:
        track_id: Tracking ID assigned to the person.
        x: Horizontal centroid coordinate.
        y: Vertical centroid coordinate.

    Returns:
        A dictionary containing the tracking ID and centroid.
    """
    return {
        "track_id": track_id,
        "centroid": (x, y),
    }


def test_left_to_right_crossing_is_counted_as_entry():
    """
    Tests that a person moving from left to right is counted as an entry.
    """

    counter = PeopleCounter(line_x=500, counting_margin=20)

    # Person starts on the left side
    counter.update([create_person(track_id=1, x=400)])

    # moves through the neutral zone
    counter.update([create_person(track_id=1, x=500)])

    # arrives on the right side
    events = counter.update([create_person(track_id=1, x=600)])

    assert counter.entries == 1
    assert counter.exits == 0

    assert len(events) == 1
    assert events[0].track_id == 1
    assert events[0].direction == "IN"


def test_right_to_left_crossing_is_counted_as_exit():
    """
    Tests that a person moving from right to left is counted as an exit.
    """

    counter = PeopleCounter(line_x=500, counting_margin=20)

    # Person starts on the right side
    counter.update([create_person(track_id=1, x=600)])

    # moves through the neutral zone
    counter.update([create_person(track_id=1, x=500)])

    # arrives on the left side
    events = counter.update([create_person(track_id=1, x=400)])

    assert counter.entries == 0
    assert counter.exits == 1

    assert len(events) == 1
    assert events[0].track_id == 1
    assert events[0].direction == "OUT"


def test_same_person_can_cross_multiple_times():
    """
    Tests that the same tracked person can generate multiple crossing events.
    """

    counter = PeopleCounter(line_x=500, counting_margin=20)

    # First crossing: left → right
    counter.update([create_person(track_id=1, x=400)])
    counter.update([create_person(track_id=1, x=500)])
    counter.update([create_person(track_id=1, x=600)])

    # Second crossing: right → left
    counter.update([create_person(track_id=1, x=500)])
    counter.update([create_person(track_id=1, x=400)])

    # Third crossing: left → right
    counter.update([create_person(track_id=1, x=500)])
    counter.update([create_person(track_id=1, x=600)])

    assert counter.entries == 2
    assert counter.exits == 1


def test_movement_inside_neutral_zone_does_not_count():
    """
    Tests that small movements around the counting line do not create events.
    """
    counter = PeopleCounter(line_x=500, counting_margin=20)

    # Start on the left
    counter.update([create_person(track_id=1, x=400)])

    # Move around inside the neutral zone
    counter.update([create_person(track_id=1, x=490)])
    counter.update([create_person(track_id=1, x=510)])
    counter.update([create_person(track_id=1, x=495)])

    assert counter.entries == 0
    assert counter.exits == 0