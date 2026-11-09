"""Nose tests for ACP brevet control times and the Flask endpoint."""

from datetime import datetime

import acp_times
from flask_brevets import app


START = "2024-01-01T00:00:00"


def elapsed_minutes(timestamp):
    """Return minutes elapsed from START."""
    start = datetime.fromisoformat(START)
    result = datetime.fromisoformat(timestamp)
    return int((result - start).total_seconds() // 60)


def test_200_km_opening_and_closing_examples():
    assert elapsed_minutes(acp_times.open_time(60, 200, START)) == 106
    assert elapsed_minutes(acp_times.close_time(60, 200, START)) == 240


def test_opening_time_uses_piecewise_speed_bands():
    assert elapsed_minutes(acp_times.open_time(350, 600, START)) == 634
    assert elapsed_minutes(acp_times.open_time(550, 600, START)) == 1028
    assert elapsed_minutes(acp_times.close_time(550, 600, START)) == 2200


def test_opening_time_uses_each_speed_band_on_1000_km_brevet():
    assert elapsed_minutes(acp_times.open_time(890, 1000, START)) == 1749
    assert elapsed_minutes(acp_times.close_time(890, 1000, START)) == 3923


def test_closing_time_uses_relaxed_rule_below_60_km():
    assert elapsed_minutes(acp_times.close_time(10, 200, START)) == 90
    assert elapsed_minutes(acp_times.close_time(59, 200, START)) == 237


def test_closing_time_returns_to_standard_rule_at_60_km():
    assert elapsed_minutes(acp_times.close_time(60, 200, START)) == 240


def test_official_brevet_finish_limits_override_calculated_times():
    for brevet_distance, expected_minutes in (
        (200, 810),
        (300, 1200),
        (400, 1620),
        (600, 2400),
        (1000, 4500),
    ):
        assert elapsed_minutes(
            acp_times.close_time(brevet_distance, brevet_distance, START)
        ) == expected_minutes


def test_finish_distance_is_capped_at_nominal_brevet_length():
    assert acp_times.open_time(205, 200, START) == acp_times.open_time(
        200, 200, START
    )
    assert acp_times.close_time(205, 200, START) == acp_times.close_time(
        200, 200, START
    )


def test_control_distance_is_truncated_to_whole_kilometers():
    assert acp_times.open_time(100.99, 300, START) == acp_times.open_time(
        100, 300, START
    )


def test_time_is_rounded_to_the_nearest_minute():
    assert elapsed_minutes(acp_times.open_time(1, 200, START)) == 2


def test_calculated_times_preserve_start_date_and_cross_midnight():
    late_start = "2024-01-01T23:00:00"
    result = datetime.fromisoformat(acp_times.open_time(200, 200, late_start))
    assert result == datetime(2024, 1, 2, 4, 53)


def test_invalid_brevet_distance_is_rejected():
    try:
        acp_times.open_time(100, 250, START)
    except ValueError:
        pass
    else:
        raise AssertionError("Unsupported brevet distance should be rejected")


def test_ajax_endpoint_uses_requested_brevet_and_start_time():
    client = app.test_client()
    response = client.get(
        "/_calc_times",
        query_string={
            "km": "100",
            "brevet_dist_km": "300",
            "start_time": "2024-01-01T06:00:00",
        },
    )

    assert response.status_code == 200
    result = response.get_json()["result"]
    assert result["open"] == "2024-01-01T08:56:00"
    assert result["close"] == "2024-01-01T12:40:00"


def test_ajax_endpoint_rejects_missing_parameters():
    response = app.test_client().get("/_calc_times", query_string={"km": "100"})

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_calculator_page_renders_ajax_form():
    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"brevet_dist_km" in response.data
    assert b"TIME_CALC_URL" in response.data


def test_opening_time_transition_at_200_km():
    assert elapsed_minutes(acp_times.open_time(200, 300, START)) == 353
    assert elapsed_minutes(acp_times.open_time(201, 300, START)) == 355


def test_opening_time_transition_at_400_km():
    assert elapsed_minutes(acp_times.open_time(400, 600, START)) == 728
    assert elapsed_minutes(acp_times.open_time(401, 600, START)) == 730


def test_opening_time_transition_at_600_km():
    assert elapsed_minutes(acp_times.open_time(600, 1000, START)) == 1128
    assert elapsed_minutes(acp_times.open_time(601, 1000, START)) == 1130


def test_closing_time_at_59_99_km_uses_truncated_distance():
    assert elapsed_minutes(acp_times.close_time(59.99, 200, START)) == 237


def test_closing_time_at_60_km_uses_standard_speed():
    assert elapsed_minutes(acp_times.close_time(60, 200, START)) == 240


def test_closing_time_at_61_km_uses_standard_speed():
    assert elapsed_minutes(acp_times.close_time(61, 200, START)) == 244


def test_negative_control_distance_is_rejected():
    try:
        acp_times.open_time(-1, 200, START)
    except ValueError:
        pass
    else:
        raise AssertionError("Negative control distance should be rejected")


def test_nan_control_distance_is_rejected():
    try:
        acp_times.open_time(float("nan"), 200, START)
    except ValueError:
        pass
    else:
        raise AssertionError("NaN control distance should be rejected")


def test_infinite_control_distance_is_rejected():
    try:
        acp_times.open_time(float("inf"), 200, START)
    except ValueError:
        pass
    else:
        raise AssertionError("Infinite control distance should be rejected")
