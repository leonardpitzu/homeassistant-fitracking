"""Tests for parsing Fi's behaviour trend payload."""

from datetime import datetime
from unittest.mock import patch

from custom_components.fitracking.behavior import fetch_behavior_events

MIDNIGHT = datetime(2026, 9, 19)

# Trimmed from a real response: Eating had one event, Licking two overlapping.
PAYLOAD = {
    "data": {
        "getPetHealthTrendsForPet": {
            "behaviorTrends": [
                {
                    "id": "eating:DAY",
                    "title": "Eating",
                    "chart": {
                        "intervals": [
                            {"intervalType": "NOTHING", "offset": 0},
                            {"intervalType": "EVENT", "offset": 5248},
                            {"intervalType": "NOTHING", "offset": 5948},
                        ]
                    },
                },
                {
                    "id": "cleaning_self:DAY",
                    "title": "Licking",
                    "chart": {
                        "intervals": [
                            {"intervalType": "EVENT", "offset": 5392},
                            {"intervalType": "EVENT", "offset": 5510},
                        ]
                    },
                },
                {"id": "barking:DAY", "title": "Barking", "chart": {"intervals": []}},
            ]
        }
    }
}


def _fetch(payload):
    with (
        patch("custom_components.fitracking.behavior.query.query", return_value=payload),
        patch(
            "custom_components.fitracking.behavior.dt_util.start_of_local_day",
            return_value=MIDNIGHT,
        ),
    ):
        return fetch_behavior_events(object(), "pet-id")


def test_only_event_intervals_are_kept():
    """NOTHING intervals are the gaps between events, not events."""
    events = _fetch(PAYLOAD)
    assert len(events["eating"]) == 1
    assert len(events["cleaning_self"]) == 2


def test_offsets_are_seconds_since_local_midnight():
    events = _fetch(PAYLOAD)
    assert events["eating"][0] == datetime(2026, 9, 19, 1, 27, 28)


def test_behaviour_key_strips_the_period_suffix():
    """Fi ids look like "cleaning_self:DAY"; the sensor keys on the stem."""
    assert set(_fetch(PAYLOAD)) == {"eating", "cleaning_self", "barking"}


def test_no_events_is_empty_not_missing():
    """A quiet behaviour must still report, so the sensor reads 0 rather than None."""
    assert _fetch(PAYLOAD)["barking"] == []


def test_empty_response_does_not_raise():
    assert _fetch({"data": {"getPetHealthTrendsForPet": None}}) == {}
