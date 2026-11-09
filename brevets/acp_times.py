"""Open and close time calculations for ACP-sanctioned brevets."""

import math
from datetime import datetime, timedelta


BREVET_DISTANCES = (200, 300, 400, 600, 1000)
FINISH_CLOSE_MINUTES = {
    200: 13 * 60 + 30,
    300: 20 * 60,
    400: 27 * 60,
    600: 40 * 60,
    1000: 75 * 60,
}
OPEN_SPEED_BANDS = ((200, 34), (400, 32), (600, 30), (1000, 28))


def _control_distance(control_dist_km, brevet_dist_km):
    """Return the whole-kilometer control distance, capped at the brevet finish."""
    try:
        distance = float(control_dist_km)
    except (TypeError, ValueError):
        raise ValueError("Control distance must be a non-negative number")
    if not math.isfinite(distance) or distance < 0:
        raise ValueError("Control distance must be a non-negative number")

    return min(int(distance), brevet_dist_km)


def _brevet_distance(brevet_dist_km):
    """Validate and return one of the official ACP brevet distances."""
    try:
        numeric_distance = float(brevet_dist_km)
    except (TypeError, ValueError):
        raise ValueError("Brevet distance must be one of 200, 300, 400, 600, or 1000")
    if not math.isfinite(numeric_distance) or not numeric_distance.is_integer():
        raise ValueError("Brevet distance must be one of 200, 300, 400, 600, or 1000")
    distance = int(numeric_distance)
    if distance not in BREVET_DISTANCES:
        raise ValueError("Brevet distance must be one of 200, 300, 400, 600, or 1000")
    return distance


def _rounded_minutes(hours):
    """Round a calculated duration to the nearest minute."""
    return int(math.floor(hours * 60 + 0.5))


def _time_at(start_time, minutes):
    """Add a duration to an ISO 8601 start time and return an ISO timestamp."""
    try:
        if not isinstance(start_time, str):
            raise TypeError
        start = datetime.fromisoformat(start_time)
    except (TypeError, ValueError) as error:
        raise ValueError("Start time must be a valid ISO 8601 date-time") from error
    if "T" not in start_time and " " not in start_time:
        raise ValueError("Start time must include both a date and a time")
    return (start + timedelta(minutes=minutes)).isoformat()


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Calculate a control's opening time from the ACP maximum-speed bands.

    Control distance is truncated to whole kilometers and capped at the
    scheduled brevet distance, so a route's over-distance finish is timed as
    the nominal brevet finish.
    """
    brevet_distance = _brevet_distance(brevet_dist_km)
    distance = _control_distance(control_dist_km, brevet_distance)

    remaining = distance
    previous_limit = 0
    elapsed_hours = 0.0
    for band_limit, speed in OPEN_SPEED_BANDS:
        band_distance = min(remaining, band_limit - previous_limit)
        elapsed_hours += band_distance / speed
        remaining -= band_distance
        previous_limit = band_limit
        if remaining == 0:
            break

    return _time_at(brevet_start_time, _rounded_minutes(elapsed_hours))


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Calculate a control's closing time from ACP minimum-speed bands.

    RUSA's relaxed rule is used below 60 km. At the scheduled brevet finish,
    the official overall time limit takes precedence over the speed calculation.
    """
    brevet_distance = _brevet_distance(brevet_dist_km)
    distance = _control_distance(control_dist_km, brevet_distance)

    if distance == brevet_distance:
        minutes = FINISH_CLOSE_MINUTES[brevet_distance]
    elif distance < 60:
        minutes = _rounded_minutes(distance / 20 + 1)
    else:
        elapsed_hours = min(distance, 600) / 15
        if distance > 600:
            elapsed_hours += (distance - 600) / 11.428
        minutes = _rounded_minutes(elapsed_hours)

    return _time_at(brevet_start_time, minutes)
