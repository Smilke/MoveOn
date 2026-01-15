"""Business rules and helper math for angle-based validation and repetition counting."""
from typing import List, Tuple
import math


def compute_angle(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
    """Compute angle ABC (in degrees) given three 2D points a,b,c.

    a, b, c are (x, y)
    """
    # vectors BA and BC
    bax = a[0] - b[0]
    bay = a[1] - b[1]
    bcx = c[0] - b[0]
    bcy = c[1] - b[1]

    dot = bax * bcx + bay * bcy
    mag1 = math.hypot(bax, bay)
    mag2 = math.hypot(bcx, bcy)
    if mag1 == 0 or mag2 == 0:
        return 0.0
    cosv = max(-1.0, min(1.0, dot / (mag1 * mag2)))
    angle_rad = math.acos(cosv)
    return math.degrees(angle_rad)


def count_reps(angle_sequence: List[Tuple[float, float]], down_threshold: float = 90.0, up_threshold: float = 160.0) -> int:
    """Count repetitions based on angle sequence.

    angle_sequence: list of (timestamp, angle_degrees)
    A repetition is counted when angle goes below down_threshold (bottom) and then above up_threshold (top).
    """
    state = "up"
    reps = 0
    for _, angle in angle_sequence:
        if state == "up" and angle <= down_threshold:
            state = "down"
        elif state == "down" and angle >= up_threshold:
            reps += 1
            state = "up"
    return reps


def segment_reps(angle_sequence: List[Tuple[float, float]], down_threshold: float = 90.0, up_threshold: float = 160.0):
    """Segment the angle sequence into repetitions.

    Returns a list of dicts with start/bottom/end timestamps and min/max angles.
    """
    reps = []
    state = "up"
    current_segment = None

    for t, angle in angle_sequence:
        if state == "up" and angle <= down_threshold:
            # started going down
            state = "down"
            current_segment = {"start": t, "bottom": t, "end": None, "min_angle": angle, "max_angle": angle}
        elif state == "down":
            # update min/max and bottom timestamp
            if current_segment is not None:
                if angle < current_segment["min_angle"]:
                    current_segment["min_angle"] = angle
                    current_segment["bottom"] = t
                if angle > current_segment["max_angle"]:
                    current_segment["max_angle"] = angle

            if angle >= up_threshold and current_segment is not None:
                # completed rep
                current_segment["end"] = t
                # ensure max_angle recorded includes this high point
                if angle > current_segment.get("max_angle", -1):
                    current_segment["max_angle"] = angle
                reps.append(current_segment)
                current_segment = None
                state = "up"

    return reps
