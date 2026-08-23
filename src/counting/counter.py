from dataclasses import dataclass
from datetime import datetime


@dataclass
class CrossingEvent:
    """
    Represents a single person crossing event.

    Args:
        track_id: Persistent ID assigned to the person by the tracker.
        direction: Direction of movement, either "IN" or "OUT".
        timestamp: Time at which the crossing was detected.

    Returns:
        A CrossingEvent object containing the crossing information.
    """

    track_id: int
    direction: str
    timestamp: datetime


class PeopleCounter:
    """
    Detects and records people crossing a vertical counting line.

    Args:
        line_x: X-coordinate of the vertical counting line.
        counting_margin: Distance around the line that is treated as a
            neutral zone to prevent false crossings caused by small movements.

    Returns:
        A PeopleCounter instance that maintains crossing events and counts.
    """

    def __init__(self, line_x: int, counting_margin: int = 20):
        self.line_x = line_x
        self.counting_margin = counting_margin

        # Store the previous x-coordinate of every tracked person
        self.previous_positions = {}

        # Store the last confirmed side of the line for every person
        self.person_sides = {}

        # Store every crossing event detected by the counter
        self.events = []

        # Total number of people who crossed from left to right
        self.entries = 0

        # Total number of people who crossed from right to left
        self.exits = 0

    def _get_side(self, x_position: int) -> str | None:
        """
        Determines which side of the counting zone a point belongs to.

        Args:
            x_position: Horizontal coordinate of the person's centroid.

        Returns:
            "left" if the point is clearly left of the zone,
            "right" if it is clearly right of the zone,
            or None if it is inside the neutral zone.
        """
        left_boundary = self.line_x - self.counting_margin
        right_boundary = self.line_x + self.counting_margin

        if x_position < left_boundary:
            return "left"

        if x_position > right_boundary:
            return "right"

        return None

    def update(self, tracked_people: list[dict]) -> list[CrossingEvent]:
        """
        Updates the counter and detects new crossing events.

        Args:
            tracked_people: List of dictionaries containing each person's
                tracking ID and centroid coordinates.

        Returns:
            A list of new CrossingEvent objects detected during this update.
        """
        new_events = []

        for person in tracked_people:
            track_id = person["track_id"]
            current_x = person["centroid"][0]

            current_side = self._get_side(current_x)

            # Initialize the person's state when we first see them
            if track_id not in self.person_sides:
                self.person_sides[track_id] = current_side
                self.previous_positions[track_id] = current_x
                continue

            previous_side = self.person_sides[track_id]

            # Update the person's position
            self.previous_positions[track_id] = current_x

            # Ignore frames where the person is inside the neutral zone
            if current_side is None:
                continue

            # If we dont yet know the person's previous side,
            # initialize it without generating an event
            if previous_side is None:
                self.person_sides[track_id] = current_side
                continue

            # left → right crossing
            if previous_side == "left" and current_side == "right":
                event = CrossingEvent(
                    track_id=track_id,
                    direction="IN",
                    timestamp=datetime.now(),
                )

                self.entries += 1
                self.events.append(event)
                new_events.append(event)

            # left ← right crossing
            elif previous_side == "right" and current_side == "left":
                event = CrossingEvent(
                    track_id=track_id,
                    direction="OUT",
                    timestamp=datetime.now(),
                )

                self.exits += 1
                self.events.append(event)
                new_events.append(event)

            # Update the confirmed side after processing the crossing
            self.person_sides[track_id] = current_side

        return new_events